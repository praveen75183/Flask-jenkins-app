from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("main", __name__)

# Simple in-memory store, enough to demonstrate a CRUD-style API in CI.
_ITEMS = {}
_NEXT_ID = 1


@bp.get("/")
def index():
    return jsonify(
        message="Hello from Flask running through Jenkins CI/CD!",
        app=current_app.config["APP_NAME"],
        version=current_app.config["APP_VERSION"],
    )


@bp.get("/health")
def health():
    """Used by Docker HEALTHCHECK, load balancers and the Jenkins smoke test."""
    return jsonify(status="ok"), 200


@bp.get("/api/items")
def list_items():
    return jsonify(list(_ITEMS.values()))


@bp.post("/api/items")
def create_item():
    global _NEXT_ID
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name or not isinstance(name, str):
        return jsonify(error="'name' is required and must be a string"), 400

    item = {"id": _NEXT_ID, "name": name}
    _ITEMS[_NEXT_ID] = item
    _NEXT_ID += 1
    return jsonify(item), 201


@bp.get("/api/items/<int:item_id>")
def get_item(item_id):
    item = _ITEMS.get(item_id)
    if item is None:
        return jsonify(error="item not found"), 404
    return jsonify(item)


@bp.delete("/api/items/<int:item_id>")
def delete_item(item_id):
    if _ITEMS.pop(item_id, None) is None:
        return jsonify(error="item not found"), 404
    return "", 204
