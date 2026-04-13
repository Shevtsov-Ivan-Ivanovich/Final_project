# server/api/characters.py
from flask import Blueprint, request, jsonify
from server.models import db, User, Character, Session, CharacterItem, Item

characters_bp = Blueprint('characters', __name__, url_prefix='/api/characters')


@characters_bp.route('/', methods=['GET'])
def get_characters():
    """Получить всех персонажей"""
    try:
        characters = Character.query.all()
        return jsonify([c.to_dict() for c in characters]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>', methods=['GET'])
def get_character(character_id):
    """Получить персонажа по ID"""
    try:
        character = Character.query.get_or_404(character_id)
        return jsonify(character.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/my/<int:user_id>', methods=['GET'])
def get_my_characters(user_id):
    """Получить персонажей пользователя"""
    try:
        characters = Character.query.filter_by(user_id=user_id).all()
        return jsonify([c.to_dict() for c in characters]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/', methods=['POST'])
def create_character():
    """Создать нового персонажа"""
    try:
        data = request.json
        
        if not data.get('name') or not data.get('user_id'):
            return jsonify({'error': 'name and user_id are required'}), 400
        
        character = Character(
            name=data['name'],
            user_id=data['user_id'],
            strength=data.get('strength', 10),
            dexterity=data.get('dexterity', 10),
            intelligence=data.get('intelligence', 10),
            charisma=data.get('charisma', 10),
            max_hp=data.get('max_hp', 10),
            max_mp=data.get('max_mp', 5),
            current_hp=data.get('max_hp', 10),
            current_mp=data.get('max_mp', 5),
            level=data.get('level', 1),
            experience=data.get('experience', 0)
        )
        
        db.session.add(character)
        db.session.commit()
        
        return jsonify({'success': True, 'character': character.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>', methods=['PUT'])
def update_character(character_id):
    """Обновить персонажа"""
    try:
        character = Character.query.get_or_404(character_id)
        data = request.json
        
        allowed_fields = ['name', 'level', 'experience', 'strength', 'dexterity', 
                         'intelligence', 'charisma', 'current_hp', 'current_mp', 
                         'max_hp', 'max_mp', 'session_id']
        
        for key, value in data.items():
            if key in allowed_fields and hasattr(character, key):
                setattr(character, key, value)
        
        # Обновляем временные метки
        from datetime import datetime
        character.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'character': character.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    """Удалить персонажа"""
    try:
        character = Character.query.get_or_404(character_id)
        
        # Проверяем, не привязан ли персонаж к активной сессии
        if character.session_id:
            session = Session.query.get(character.session_id)
            if session and session.is_active:
                return jsonify({'error': 'Cannot delete character while in active session'}), 400
        
        # Удаляем связанные предметы
        CharacterItem.query.filter_by(character_id=character_id).delete()
        
        db.session.delete(character)
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>/inventory', methods=['GET'])
def get_character_inventory(character_id):
    """Получить инвентарь персонажа"""
    try:
        items = CharacterItem.query.filter_by(character_id=character_id).all()
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>/add_item', methods=['POST'])
def add_item_to_character(character_id):
    """Добавить предмет персонажу"""
    try:
        data = request.json
        item_id = data.get('item_id')
        quantity = data.get('quantity', 1)
        
        if not item_id:
            return jsonify({'error': 'item_id is required'}), 400
        
        character = Character.query.get_or_404(character_id)
        item = Item.query.get_or_404(item_id)
        
        existing = CharacterItem.query.filter_by(
            character_id=character_id, 
            item_id=item_id
        ).first()
        
        if existing:
            existing.quantity += quantity
        else:
            existing = CharacterItem(
                character_id=character_id,
                item_id=item_id,
                quantity=quantity
            )
            db.session.add(existing)
        
        db.session.commit()
        return jsonify({'success': True, 'item': existing.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>/remove_item/<int:item_id>', methods=['DELETE'])
def remove_item_from_character(character_id, item_id):
    """Удалить предмет у персонажа"""
    try:
        item = CharacterItem.query.filter_by(
            character_id=character_id, 
            item_id=item_id
        ).first()
        
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        if item.quantity > 1:
            item.quantity -= 1
            db.session.commit()
        else:
            db.session.delete(item)
            db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>/equip/<int:item_id>', methods=['POST'])
def equip_item(character_id, item_id):
    """Экипировать предмет"""
    try:
        character_item = CharacterItem.query.filter_by(
            character_id=character_id, 
            item_id=item_id
        ).first()
        
        if not character_item:
            return jsonify({'error': 'Item not found'}), 404
        
        item = Item.query.get(item_id)
        if not item or not item.is_equippable:
            return jsonify({'error': 'Item cannot be equipped'}), 400
        
        # Снимаем предмет с того же слота, если он есть
        slot = item.slot
        if slot:
            equipped = CharacterItem.query.filter_by(
                character_id=character_id,
                is_equipped=True
            ).all()
            
            for eq in equipped:
                eq_item = Item.query.get(eq.item_id)
                if eq_item and eq_item.slot == slot:
                    eq.is_equipped = False
        
        character_item.is_equipped = True
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>/unequip/<int:item_id>', methods=['POST'])
def unequip_item(character_id, item_id):
    """Снять экипировку с предмета"""
    try:
        character_item = CharacterItem.query.filter_by(
            character_id=character_id, 
            item_id=item_id
        ).first()
        
        if not character_item:
            return jsonify({'error': 'Item not found'}), 404
        
        character_item.is_equipped = False
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/attach_to_session', methods=['POST'])
def attach_to_session():
    """Привязать персонажа к сессии"""
    try:
        data = request.json
        character_id = data.get('character_id')
        session_id = data.get('session_id')
        
        if not character_id or not session_id:
            return jsonify({'error': 'character_id and session_id are required'}), 400
        
        character = Character.query.get_or_404(character_id)
        session = Session.query.get_or_404(session_id)
        
        # Проверяем, не привязан ли уже персонаж
        if character.session_id:
            return jsonify({'error': 'Character already attached to a session'}), 400
        
        character.session_id = session_id
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/detach_from_session', methods=['POST'])
def detach_from_session():
    """Отвязать персонажа от сессии"""
    try:
        data = request.json
        character_id = data.get('character_id')
        
        if not character_id:
            return jsonify({'error': 'character_id is required'}), 400
        
        character = Character.query.get_or_404(character_id)
        character.session_id = None
        db.session.commit()
        
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@characters_bp.route('/<int:character_id>/use_item/<int:item_id>', methods=['POST'])
def use_consumable(character_id, item_id):
    """Использовать расходный предмет"""
    try:
        character_item = CharacterItem.query.filter_by(
            character_id=character_id, 
            item_id=item_id
        ).first()
        
        if not character_item:
            return jsonify({'error': 'Item not found'}), 404
        
        item = Item.query.get(item_id)
        if not item or item.item_type != 'consumable':
            return jsonify({'error': 'Item is not consumable'}), 400
        
        character = Character.query.get_or_404(character_id)
        effects = item.effects or {}
        
        # Применяем эффекты
        if 'heal_hp' in effects:
            new_hp = min(character.current_hp + effects['heal_hp'], character.max_hp)
            character.current_hp = new_hp
        
        if 'heal_mp' in effects:
            new_mp = min(character.current_mp + effects['heal_mp'], character.max_mp)
            character.current_mp = new_mp
        
        # Удаляем использованный предмет
        if character_item.quantity > 1:
            character_item.quantity -= 1
        else:
            db.session.delete(character_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'effects': effects,
            'new_hp': character.current_hp,
            'new_mp': character.current_mp
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500