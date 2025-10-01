"""
MinIO service for handling file uploads, storage, and serving media files.
"""

import hashlib
import uuid
from datetime import timedelta
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error
from PIL import Image
import io

from config import Config


class MinIOService:
    """Service class for MinIO operations."""
    
    def __init__(self):
        self.client = Minio(
            Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS_KEY,
            secret_key=Config.MINIO_SECRET_KEY,
            secure=Config.MINIO_SECURE
        )
        self.bucket_name = Config.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                print(f"Created MinIO bucket: {self.bucket_name}")
            else:
                print(f"MinIO bucket already exists: {self.bucket_name}")
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")
            raise
    
    def generate_presigned_upload_url(self, object_name: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Generate a pre-signed URL for uploading a file."""
        try:
            url = self.client.presigned_put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned upload URL: {e}")
            raise
    
    def generate_presigned_get_url(self, object_name: str, expires: timedelta = timedelta(hours=24)) -> str:
        """Generate a pre-signed URL for downloading/viewing a file."""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                expires=expires
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned get URL: {e}")
            raise
    
    def upload_file(self, file_data: BinaryIO, object_name: str, content_type: str = None) -> dict:
        """Upload a file directly to MinIO."""
        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning
            
            # Upload file
            result = self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type
            )
            
            return {
                "object_name": object_name,
                "bucket_name": self.bucket_name,
                "size": file_size,
                "etag": result.etag,
                "url": self.generate_presigned_get_url(object_name)
            }
            
        except S3Error as e:
            print(f"Error uploading file: {e}")
            raise
    
    def delete_file(self, object_name: str):
        """Delete a file from MinIO."""
        try:
            self.client.remove_object(self.bucket_name, object_name)
            print(f"Deleted file: {object_name}")
        except S3Error as e:
            print(f"Error deleting file: {e}")
            raise
    
    def generate_thumbnail(self, image_data: BinaryIO, max_size: tuple = (300, 300)) -> bytes:
        """Generate a thumbnail from an image."""
        try:
            # Open image
            image = Image.open(image_data)
            
            # Convert to RGB if needed (for PNG with transparency, etc.)
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Create thumbnail
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.getvalue()
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            raise
    
    def calculate_file_hash(self, file_data: BinaryIO) -> str:
        """Calculate SHA-256 hash of file content for deduplication."""
        file_data.seek(0)
        hasher = hashlib.sha256()
        
        for chunk in iter(lambda: file_data.read(4096), b""):
            hasher.update(chunk)
        
        file_data.seek(0)
        return hasher.hexdigest()
    
    def generate_object_name(self, user_id: int, original_filename: str, file_hash: str = None) -> str:
        """Generate a unique object name for a file."""
        # Extract file extension
        ext = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
        
        # Use file hash if provided, otherwise generate UUID
        unique_id = file_hash[:16] if file_hash else str(uuid.uuid4())
        
        # Format: submissions/{user_id}/{unique_id}.{ext}
        return f"submissions/{user_id}/{unique_id}.{ext}"
    
    def generate_thumbnail_name(self, original_object_name: str) -> str:
        """Generate thumbnail object name from original."""
        base_name, ext = original_object_name.rsplit('.', 1) if '.' in original_object_name else (original_object_name, '')
        return f"{base_name}_thumb.jpg"


# Global MinIO service instance
minio_service = MinIOService()