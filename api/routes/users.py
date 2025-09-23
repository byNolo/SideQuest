from . import bp
from flask import jsonify
from seed_templates import seed_templates

@bp.get("/health")
def health():
    return jsonify({"ok": True})

@bp.post("/admin/seed-templates")
def admin_seed_templates():
    """Admin endpoint to seed quest templates"""
    try:
        seed_templates()
        return jsonify({"ok": True, "message": "Templates seeded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
