"""
Submission routes for creating and managing quest submissions.
"""

from datetime import datetime, date
from flask import request, jsonify

from auth import login_required, require_user  
from database import session_scope
from models import Submission, Quest, User
from . import bp


@bp.route("/submissions", methods=["POST"])
@login_required
def create_submission():
    """Create a new quest submission."""
    user = require_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request data required"}), 400
    
    quest_id = data.get('quest_id')
    caption = data.get('caption', '').strip()
    media = data.get('media', [])  # List of media file objects
    
    if not quest_id:
        return jsonify({"error": "quest_id is required"}), 400
    
    if len(caption) > 500:
        return jsonify({"error": "Caption too long (max 500 characters)"}), 400
    
    with session_scope() as session:
        # Verify quest exists and belongs to user
        quest = session.query(Quest).filter(
            Quest.id == quest_id,
            Quest.user_id == user.id
        ).first()
        
        if not quest:
            return jsonify({"error": "Quest not found or not owned by user"}), 404
        
        # Check if submission already exists for this quest
        existing = session.query(Submission).filter(
            Submission.quest_id == quest_id
        ).first()
        
        if existing:
            return jsonify({"error": "Submission already exists for this quest"}), 409
        
        # Create submission
        submission = Submission(
            quest_id=quest_id,
            user_id=user.id,
            caption=caption or None,
            media=media,
            status="pending"
        )
        
        session.add(submission)
        
        # Update quest status
        quest.status = "submitted"
        
        session.commit()
        
        return jsonify({
            "submission": {
                "id": submission.id,
                "quest_id": submission.quest_id,
                "user_id": submission.user_id,
                "caption": submission.caption,
                "media": submission.media,
                "status": submission.status,
                "created_at": submission.created_at.isoformat()
            }
        }), 201


@bp.route("/submissions/<int:submission_id>", methods=["GET"])
@login_required
def get_submission(submission_id: int):
    """Get a specific submission."""
    user = require_user()
    
    with session_scope() as session:
        submission = session.query(Submission).filter(
            Submission.id == submission_id
        ).first()
        
        if not submission:
            return jsonify({"error": "Submission not found"}), 404
        
        # For now, allow anyone to view submissions (will add privacy controls later)
        return jsonify({
            "submission": {
                "id": submission.id,
                "quest_id": submission.quest_id,
                "user_id": submission.user_id,
                "caption": submission.caption,
                "media": submission.media,
                "status": submission.status,
                "score_cache": submission.score_cache,
                "ratings_count": submission.ratings_count,
                "created_at": submission.created_at.isoformat()
            }
        })


@bp.route("/submissions/<int:submission_id>", methods=["PATCH"])
@login_required
def update_submission(submission_id: int):
    """Update a submission (owner only)."""
    user = require_user()
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request data required"}), 400
    
    with session_scope() as session:
        submission = session.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == user.id
        ).first()
        
        if not submission:
            return jsonify({"error": "Submission not found or not owned by user"}), 404
        
        # Update fields if provided
        if 'caption' in data:
            caption = data['caption'].strip() if data['caption'] else None
            if caption and len(caption) > 500:
                return jsonify({"error": "Caption too long (max 500 characters)"}), 400
            submission.caption = caption
        
        if 'media' in data:
            submission.media = data['media']
        
        session.commit()
        
        return jsonify({
            "submission": {
                "id": submission.id,
                "quest_id": submission.quest_id,
                "user_id": submission.user_id,
                "caption": submission.caption,
                "media": submission.media,
                "status": submission.status,
                "score_cache": submission.score_cache,
                "ratings_count": submission.ratings_count,
                "created_at": submission.created_at.isoformat()
            }
        })


@bp.route("/submissions/<int:submission_id>", methods=["DELETE"])
@login_required
def delete_submission(submission_id: int):
    """Delete a submission (owner only)."""
    user = require_user()
    
    with session_scope() as session:
        submission = session.query(Submission).filter(
            Submission.id == submission_id,
            Submission.user_id == user.id
        ).first()
        
        if not submission:
            return jsonify({"error": "Submission not found or not owned by user"}), 404
        
        # Update quest status back to assigned
        quest = session.query(Quest).filter(Quest.id == submission.quest_id).first()
        if quest:
            quest.status = "assigned"
        
        session.delete(submission)
        session.commit()
        
        return jsonify({"message": "Submission deleted successfully"})


@bp.route("/submissions/feed", methods=["GET"])
@login_required  
def get_submissions_feed():
    """Get global submissions feed."""
    user = require_user()
    
    # Query parameters
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 20)), 50)  # Max 50 per page
    offset = (page - 1) * limit
    
    with session_scope() as session:
        # Get visible submissions ordered by creation time (newest first)
        submissions_query = session.query(Submission).filter(
            Submission.status == 'visible'
        ).order_by(Submission.created_at.desc())
        
        # Get total count for pagination
        total_count = submissions_query.count()
        
        # Get paginated results
        submissions = submissions_query.offset(offset).limit(limit).all()
        
        # Get user information for each submission
        user_ids = [s.user_id for s in submissions]
        users_dict = {}
        if user_ids:
            users = session.query(User).filter(User.id.in_(user_ids)).all()
            users_dict = {u.id: u for u in users}
        
        # Format response
        feed_items = []
        for submission in submissions:
            submitter = users_dict.get(submission.user_id)
            
            feed_items.append({
                "submission": {
                    "id": submission.id,
                    "quest_id": submission.quest_id,
                    "caption": submission.caption,
                    "media": submission.media,
                    "score_cache": submission.score_cache,
                    "ratings_count": submission.ratings_count,
                    "created_at": submission.created_at.isoformat()
                },
                "user": {
                    "id": submitter.id,
                    "username": submitter.username,
                    "display_name": submitter.display_name,
                    "avatar_url": submitter.avatar_url
                } if submitter else None
            })
        
        return jsonify({
            "feed": feed_items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit,
                "has_next": offset + limit < total_count,
                "has_prev": page > 1
            }
        })


@bp.route("/submissions/my", methods=["GET"])
@login_required
def get_my_submissions():
    """Get current user's submissions."""
    user = require_user()
    
    # Query parameters
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 20)), 50)
    offset = (page - 1) * limit
    
    with session_scope() as session:
        # Get user's submissions
        submissions_query = session.query(Submission).filter(
            Submission.user_id == user.id
        ).order_by(Submission.created_at.desc())
        
        total_count = submissions_query.count()
        submissions = submissions_query.offset(offset).limit(limit).all()
        
        # Get associated quests for context
        quest_ids = [s.quest_id for s in submissions]
        quests_dict = {}
        if quest_ids:
            quests = session.query(Quest).filter(Quest.id.in_(quest_ids)).all()
            quests_dict = {q.id: q for q in quests}
        
        # Format response
        items = []
        for submission in submissions:
            quest = quests_dict.get(submission.quest_id)
            
            items.append({
                "submission": {
                    "id": submission.id,
                    "quest_id": submission.quest_id,
                    "caption": submission.caption,
                    "media": submission.media,
                    "status": submission.status,
                    "score_cache": submission.score_cache,
                    "ratings_count": submission.ratings_count,
                    "created_at": submission.created_at.isoformat()
                },
                "quest": {
                    "id": quest.id,
                    "date": quest.date.isoformat(),
                    "generated_context": quest.generated_context,
                    "status": quest.status
                } if quest else None
            })
        
        return jsonify({
            "submissions": items,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_count,
                "pages": (total_count + limit - 1) // limit,
                "has_next": offset + limit < total_count,
                "has_prev": page > 1
            }
        })