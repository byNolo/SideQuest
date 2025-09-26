from flask import jsonify

from . import bp


@bp.get("/health")
def health_check():
    return jsonify({"ok": True})
