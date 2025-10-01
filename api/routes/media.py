"""
Media upload and management routes for handling file uploads to MinIO.
"""

import os
from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename

from auth import login_required, require_user
from minio_service import minio_service
from database import session_scope
from models import Submission
from . import bp


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/media/upload-url", methods=["POST"])
@login_required
def get_upload_url():
    """Generate pre-signed URL for file upload."""
    user = require_user()
    data = request.get_json()
    
    if not data or 'filename' not in data:
        return jsonify({"error": "Filename is required"}), 400
    
    filename = secure_filename(data['filename'])
    if not filename or not allowed_file(filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    # Generate unique object name
    object_name = minio_service.generate_object_name(user.id, filename)
    
    try:
        # Generate pre-signed upload URL
        upload_url = minio_service.generate_presigned_upload_url(object_name)
        
        return jsonify({
            "upload_url": upload_url,
            "object_name": object_name,
            "expires_in": 3600  # 1 hour
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to generate upload URL: {str(e)}"}), 500


@bp.route("/media/upload", methods=["POST"])
@login_required  
def upload_media():
    """Direct file upload endpoint (alternative to pre-signed URLs)."""
    user = require_user()
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": "File too large"}), 400
    
    try:
        # Calculate file hash for deduplication
        file_hash = minio_service.calculate_file_hash(file)
        
        # Generate object name
        object_name = minio_service.generate_object_name(user.id, file.filename, file_hash)
        
        # Upload file
        file_info = minio_service.upload_file(
            file_data=file,
            object_name=object_name,
            content_type=file.content_type
        )
        
        # Generate thumbnail for images
        thumbnail_url = None
        if file.content_type and file.content_type.startswith('image/'):
            try:
                file.seek(0)
                thumbnail_data = minio_service.generate_thumbnail(file)
                thumbnail_name = minio_service.generate_thumbnail_name(object_name)
                
                # Upload thumbnail
                thumbnail_info = minio_service.upload_file(
                    file_data=thumbnail_data,
                    object_name=thumbnail_name,
                    content_type='image/jpeg'
                )
                thumbnail_url = thumbnail_info['url']
                
            except Exception as e:
                print(f"Failed to generate thumbnail: {e}")
        
        return jsonify({
            "file_info": file_info,
            "thumbnail_url": thumbnail_url,
            "file_hash": file_hash,
            "content_type": file.content_type
        })
        
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@bp.route("/media/<path:object_name>", methods=["GET"])
def get_media_url(object_name: str):
    """Get pre-signed URL for accessing media file."""
    try:
        # Generate pre-signed URL for viewing
        media_url = minio_service.generate_presigned_get_url(object_name)
        
        return jsonify({
            "url": media_url,
            "object_name": object_name
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get media URL: {str(e)}"}), 500


@bp.route("/media/<path:object_name>", methods=["DELETE"])
@login_required
def delete_media(object_name: str):
    """Delete media file (only owner can delete)."""
    user = require_user()
    
    # Check if user owns this file (object name contains user ID)
    if not object_name.startswith(f"submissions/{user.id}/"):
        return jsonify({"error": "Not authorized to delete this file"}), 403
    
    try:
        # Delete main file
        minio_service.delete_file(object_name)
        
        # Try to delete thumbnail if it exists
        thumbnail_name = minio_service.generate_thumbnail_name(object_name)
        try:
            minio_service.delete_file(thumbnail_name)
        except:
            pass  # Thumbnail might not exist
        
        return jsonify({"message": "File deleted successfully"})
        
    except Exception as e:
        return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500