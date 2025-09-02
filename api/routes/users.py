from . import bp
from flask import jsonify

@bp.get("/health")
def health():
    return jsonify({"ok": True})
