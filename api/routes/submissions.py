from . import bp
from flask import jsonify, request

@bp.post("/submissions")
def create_submission():
    data = request.json or {}
    # TODO: validate & persist, kick off Celery post-process
    return jsonify({"ok": True, "id": 1, "echo": data})
