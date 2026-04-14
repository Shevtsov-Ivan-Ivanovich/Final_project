# server/api/items.py
from flask import Blueprint, request, jsonify
from server.models import db, Item

items_bp = Blueprint('items', __name__, url_prefix='/api/items')


@items_bp.route('/', methods=['GET'])
def get_items():
    items = Item.query.all()
    return jsonify([i.to_dict() for i in items]), 200


@items_bp.route('/', methods=['POST'])
def create_item():
    data = request.json
    
    item = Item(
        name=data['name'],
        description=data.get('description', ''),
        item_type=data.get('item_type', 'misc'),
        slot=data.get('slot'),
        effects=data.get('effects', {}),
        icon=data.get('icon', '📦'),
        is_equippable=data.get('is_equippable', True),
        value=data.get('value', 0)
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify({'success': True, 'item': item.to_dict()}), 201


@items_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True}), 200