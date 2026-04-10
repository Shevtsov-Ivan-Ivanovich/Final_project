# server/api/game.py
from flask import Blueprint, request, jsonify
from server.models import db, Character, Session, GameLog, CharacterItem, Item
from datetime import datetime

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


@game_bp.route('/session/<int:session_id>/state', methods=['GET'])
def get_session_state(session_id):
    """Получить состояние сессии (персонажи, их статы, инвентарь)"""
    try:
        session = Session.query.get_or_404(session_id)
        
        characters = Character.query.filter_by(session_id=session_id).all()
        characters_data = []
        
        for char in characters:
            # Получаем инвентарь
            inventory = CharacterItem.query.filter_by(character_id=char.id).all()
            
            characters_data.append({
                'character': char.to_dict(),
                'inventory': [item.to_dict() for item in inventory]
            })
        
        return jsonify({
            'session': session.to_dict(),
            'characters': characters_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/character/<int:character_id>/full', methods=['GET'])
def get_character_full(character_id):
    """Получить полные данные персонажа (статы + инвентарь)"""
    try:
        character = Character.query.get_or_404(character_id)
        inventory = CharacterItem.query.filter_by(character_id=character_id).all()
        
        return jsonify({
            'character': character.to_dict(),
            'inventory': [item.to_dict() for item in inventory]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/session/<int:session_id>/logs', methods=['GET'])
def get_session_game_logs(session_id):
    """Получить игровые логи сессии"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        logs = GameLog.query.filter_by(session_id=session_id)\
            .order_by(GameLog.timestamp.desc())\
            .limit(limit).all()
        
        return jsonify([log.to_dict() for log in logs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/character/<int:character_id>/action', methods=['POST'])
def perform_action(character_id):
    """Выполнить игровое действие"""
    try:
        data = request.json
        action_type = data.get('action_type')
        target_id = data.get('target_id')
        details = data.get('details', {})
        
        character = Character.query.get_or_404(character_id)
        
        # Логируем действие
        log = GameLog(
            action_type=action_type,
            performer_id=character.user_id,
            target_id=target_id,
            character_id=character_id,
            session_id=character.session_id,
            details=details,
            message=data.get('message', '')
        )
        db.session.add(log)
        db.session.commit()
        
        # Обрабатываем специальные действия
        result = {'success': True, 'action': action_type}
        
        if action_type == 'heal':
            # Лечение
            heal_amount = details.get('amount', 10)
            new_hp = min(character.current_hp + heal_amount, character.max_hp)
            character.current_hp = new_hp
            result['new_hp'] = new_hp
            result['healed'] = new_hp - character.current_hp
            db.session.commit()
        
        elif action_type == 'rest':
            # Отдых - полное восстановление
            character.current_hp = character.max_hp
            character.current_mp = character.max_mp
            db.session.commit()
            result['message'] = 'Полное восстановление'
        
        elif action_type == 'level_up':
            # Повышение уровня
            character.level += 1
            # Увеличиваем характеристики
            character.strength += 1
            character.dexterity += 1
            character.intelligence += 1
            character.charisma += 1
            # Увеличиваем HP и MP
            character.max_hp += 5
            character.max_mp += 3
            character.current_hp = character.max_hp
            character.current_mp = character.max_mp
            db.session.commit()
            result['new_level'] = character.level
            result['message'] = f'Поздравляем! Вы достигли {character.level} уровня!'
        
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@game_bp.route('/roll_dice', methods=['POST'])
def roll_dice():
    """Бросок кубика"""
    try:
        import random
        import re
        
        data = request.json
        expression = data.get('expression', '1d20')
        character_id = data.get('character_id')
        
        # Парсим выражение типа "2d6+3" или "1d20"
        match = re.match(r'(\d+)d(\d+)(?:([+-])(\d+))?', expression.lower())
        
        if not match:
            return jsonify({'error': 'Invalid dice expression'}), 400
        
        num = int(match.group(1))
        sides = int(match.group(2))
        modifier = 0
        sign = match.group(3) if match.group(3) else ''
        mod_value = int(match.group(4)) if match.group(4) else 0
        
        if sign == '-':
            modifier = -mod_value
        else:
            modifier = mod_value
        
        # Ограничиваем количество кубиков
        num = min(num, 20)
        
        rolls = [random.randint(1, sides) for _ in range(num)]
        total = sum(rolls) + modifier
        
        result = {
            'expression': expression,
            'rolls': rolls,
            'modifier': modifier,
            'total': total,
            'timestamp': datetime.now().isoformat()
        }
        
        # Логируем бросок
        if character_id:
            character = Character.query.get(character_id)
            if character:
                log = GameLog(
                    action_type='dice_roll',
                    performer_id=character.user_id,
                    character_id=character_id,
                    session_id=character.session_id,
                    details=result,
                    message=f'Бросок {expression}: {total}'
                )
                db.session.add(log)
                db.session.commit()
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/session/<int:session_id>/active_players', methods=['GET'])
def get_active_players(session_id):
    """Получить активных игроков в сессии (через WebSocket)"""
    try:
        # Эта информация должна приходить из socket_routes
        # Здесь возвращаем базовую информацию из БД
        session = Session.query.get_or_404(session_id)
        characters = Character.query.filter_by(session_id=session_id).all()
        
        players = []
        for char in characters:
            players.append({
                'character_id': char.id,
                'character_name': char.name,
                'user_id': char.user_id,
                'level': char.level,
                'current_hp': char.current_hp,
                'max_hp': char.max_hp
            })
        
        return jsonify({
            'session_id': session_id,
            'session_name': session.name,
            'players': players,
            'count': len(players)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/items/all', methods=['GET'])
def get_all_game_items():
    """Получить все доступные предметы в игре"""
    try:
        items = Item.query.all()
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/items/categories', methods=['GET'])
def get_item_categories():
    """Получить категории предметов"""
    try:
        categories = {
            'weapon': '⚔️ Оружие',
            'armor': '🛡️ Броня',
            'consumable': '🧪 Расходники',
            'accessory': '💍 Аксессуары',
            'misc': '📦 Прочее'
        }
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@game_bp.route('/stats/calculate', methods=['POST'])
def calculate_stats():
    """Рассчитать итоговые характеристики с учетом экипировки"""
    try:
        data = request.json
        character_id = data.get('character_id')
        
        character = Character.query.get_or_404(character_id)
        inventory = CharacterItem.query.filter_by(character_id=character_id, is_equipped=True).all()
        
        # Базовые характеристики
        stats = {
            'strength': character.strength,
            'dexterity': character.dexterity,
            'intelligence': character.intelligence,
            'charisma': character.charisma,
            'max_hp': character.max_hp,
            'max_mp': character.max_mp
        }
        
        # Применяем бонусы от экипировки
        for item in inventory:
            item_data = Item.query.get(item.item_id)
            if item_data and item_data.effects:
                for key, value in item_data.effects.items():
                    if key in stats:
                        stats[key] += value
        
        # Рассчитываем итоговые показатели
        final_stats = {
            'strength': stats['strength'],
            'dexterity': stats['dexterity'],
            'intelligence': stats['intelligence'],
            'charisma': stats['charisma'],
            'max_hp': stats['max_hp'] + (stats['strength'] - 10) * 2,
            'max_mp': stats['max_mp'] + (stats['intelligence'] - 10) * 2,
            'attack_bonus': (stats['strength'] - 10) // 2,
            'defense_bonus': (stats['dexterity'] - 10) // 2,
            'magic_bonus': (stats['intelligence'] - 10) // 2
        }
        
        return jsonify(final_stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500