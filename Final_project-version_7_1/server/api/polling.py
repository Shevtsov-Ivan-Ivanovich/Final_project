# server/api/polling.py
from flask import Blueprint, request, jsonify
from datetime import datetime
import threading
import time
from collections import deque
import json

polling_bp = Blueprint('polling', __name__, url_prefix='/api/polling')

# Хранилище сообщений
class MessageQueue:
    def __init__(self, max_size=1000):
        self.messages = deque(maxlen=max_size)
        self.last_id = 0
        self.lock = threading.Lock()
    
    def add_message(self, message):
        with self.lock:
            self.last_id += 1
            message['id'] = self.last_id
            message['timestamp'] = datetime.now().isoformat()
            self.messages.append(message)
            return self.last_id
    
    def get_messages(self, last_id=0):
        with self.lock:
            result = []
            for msg in self.messages:
                if msg['id'] > last_id:
                    result.append(msg)
            return result

# Хранилище для каждой сессии
session_queues = {}
session_lock = threading.Lock()

# Активные соединения
active_connections = {}

def get_queue(session_id):
    with session_lock:
        if session_id not in session_queues:
            session_queues[session_id] = MessageQueue()
        return session_queues[session_id]

@polling_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()}), 200

@polling_bp.route('/register_gm', methods=['POST'])
def register_gm():
    """Регистрация ГМ в сессии"""
    data = request.json
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    username = data.get('username')
    
    if not all([session_id, user_id, username]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    with session_lock:
        if session_id not in active_connections:
            active_connections[session_id] = {
                'gm': {'user_id': user_id, 'username': username, 'sid': None},
                'players': {},
                'created_at': datetime.now().isoformat()
            }
        else:
            active_connections[session_id]['gm'] = {
                'user_id': user_id, 'username': username, 'sid': None
            }
    
    # Добавляем системное сообщение
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'system',
        'data': {'message': f'ГМ {username} присоединился к сессии'}
    })
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/register_player', methods=['POST'])
def register_player():
    """Регистрация игрока в сессии"""
    data = request.json
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    username = data.get('username')
    character_id = data.get('character_id')
    character_name = data.get('character_name')
    
    if not all([session_id, user_id, username, character_id, character_name]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    with session_lock:
        if session_id not in active_connections:
            active_connections[session_id] = {
                'gm': None,
                'players': {},
                'created_at': datetime.now().isoformat()
            }
        
        active_connections[session_id]['players'][user_id] = {
            'user_id': user_id,
            'username': username,
            'character_id': character_id,
            'character_name': character_name,
            'joined_at': datetime.now().isoformat()
        }
    
    # Добавляем сообщение о присоединении
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'player_joined',
        'data': {
            'user_id': user_id,
            'username': username,
            'character_id': character_id,
            'character_name': character_name,
            'message': f'{character_name} присоединился к сессии!'
        }
    })
    
    # Отправляем обновленный список игроков
    send_players_list(session_id)
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/disconnect', methods=['POST'])
def disconnect():
    """Отключение от сессии"""
    data = request.json
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if not session_id or not user_id:
        return jsonify({'error': 'Missing fields'}), 400
    
    with session_lock:
        if session_id in active_connections:
            # Проверяем, не ГМ ли это
            gm = active_connections[session_id].get('gm')
            if gm and gm.get('user_id') == user_id:
                active_connections[session_id]['gm'] = None
                queue = get_queue(session_id)
                queue.add_message({
                    'type': 'gm_disconnected',
                    'data': {'message': 'ГМ покинул сессию'}
                })
            else:
                # Удаляем игрока
                if user_id in active_connections[session_id]['players']:
                    player = active_connections[session_id]['players'].pop(user_id)
                    queue = get_queue(session_id)
                    queue.add_message({
                        'type': 'player_disconnected',
                        'data': {
                            'user_id': user_id,
                            'character_name': player['character_name'],
                            'message': f"{player['character_name']} покинул сессию"
                        }
                    })
                    send_players_list(session_id)
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/messages', methods=['GET'])
def get_messages():
    """Получение новых сообщений (long polling)"""
    session_id = request.args.get('session_id', type=int)
    user_id = request.args.get('user_id', type=int)
    last_id = request.args.get('last_id', 0, type=int)
    
    if not session_id or not user_id:
        return jsonify({'error': 'Missing parameters'}), 400
    
    queue = get_queue(session_id)
    
    # Long polling - ждем новые сообщения до 30 секунд
    timeout = 30
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        messages = queue.get_messages(last_id)
        if messages:
            return jsonify(messages), 200
        time.sleep(0.5)
    
    # Таймаут - возвращаем пустой список
    return jsonify([]), 200

@polling_bp.route('/send_chat', methods=['POST'])
def send_chat():
    """Отправка сообщения в чат"""
    data = request.json
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    message = data.get('message', '').strip()
    action_type = data.get('action_type', 'chat')
    
    if not all([session_id, user_id]) or not message:
        return jsonify({'error': 'Missing fields'}), 400
    
    with session_lock:
        # Определяем отправителя
        is_gm = False
        username = None
        character_name = None
        
        session_data = active_connections.get(session_id, {})
        
        # Проверяем ГМ
        gm = session_data.get('gm')
        if gm and gm.get('user_id') == user_id:
            is_gm = True
            username = gm.get('username')
            character_name = 'GM'
        
        # Проверяем игроков
        if not is_gm:
            player = session_data.get('players', {}).get(user_id)
            if player:
                username = player.get('username')
                character_name = player.get('character_name')
        
        if not username:
            return jsonify({'error': 'User not in session'}), 400
    
    # Добавляем сообщение в очередь
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'chat_message',
        'data': {
            'user_id': user_id,
            'username': username,
            'character_name': character_name,
            'message': message,
            'action_type': action_type,
            'is_gm': is_gm,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    })
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/gm_update_character', methods=['POST'])
def gm_update_character():
    """ГМ обновляет характеристики персонажа"""
    data = request.json
    session_id = data.get('session_id')
    character_id = data.get('character_id')
    updates = data.get('updates', {})
    
    if not all([session_id, character_id]):
        return jsonify({'error': 'Missing fields'}), 400
    
    # Здесь нужно обновить в БД
    from server.models import db, Character
    character = Character.query.get(character_id)
    if character:
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)
        db.session.commit()
    
    # Отправляем обновление всем в сессии
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'character_updated',
        'data': {
            'character_id': character_id,
            'character_name': character.name if character else 'Unknown',
            'updates': updates,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    })
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/gm_add_item', methods=['POST'])
def gm_add_item():
    """ГМ добавляет предмет персонажу"""
    data = request.json
    session_id = data.get('session_id')
    character_id = data.get('character_id')
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    if not all([session_id, character_id, item_id]):
        return jsonify({'error': 'Missing fields'}), 400
    
    from server.models import db, CharacterItem
    existing = CharacterItem.query.filter_by(character_id=character_id, item_id=item_id).first()
    
    if existing:
        existing.quantity += quantity
    else:
        existing = CharacterItem(character_id=character_id, item_id=item_id, quantity=quantity)
        db.session.add(existing)
    db.session.commit()
    
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'item_added',
        'data': {
            'character_id': character_id,
            'item_id': item_id,
            'quantity': quantity,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    })
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/gm_remove_item', methods=['POST'])
def gm_remove_item():
    """ГМ удаляет предмет у персонажа"""
    data = request.json
    session_id = data.get('session_id')
    character_id = data.get('character_id')
    item_id = data.get('item_id')
    
    if not all([session_id, character_id, item_id]):
        return jsonify({'error': 'Missing fields'}), 400
    
    from server.models import db, CharacterItem
    item = CharacterItem.query.filter_by(character_id=character_id, item_id=item_id).first()
    
    if item:
        if item.quantity > 1:
            item.quantity -= 1
        else:
            db.session.delete(item)
        db.session.commit()
    
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'item_removed',
        'data': {
            'character_id': character_id,
            'item_id': item_id,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    })
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/add_game_object', methods=['POST'])
def add_game_object():
    """Добавляет игровой объект"""
    data = request.json
    session_id = data.get('session_id')
    obj_type = data.get('type')
    name = data.get('name')
    description = data.get('description', '')
    obj_data = data.get('data', {})
    
    if not all([session_id, obj_type, name]):
        return jsonify({'error': 'Missing fields'}), 400
    
    from server.models import db, GameContext
    context = GameContext(
        session_id=session_id,
        context_type=obj_type,
        name=name,
        description=description,
        data=obj_data
    )
    db.session.add(context)
    db.session.commit()
    
    queue = get_queue(session_id)
    queue.add_message({
        'type': 'game_object_added',
        'data': {
            'type': obj_type,
            'name': name,
            'description': description,
            'data': context.to_dict(),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    })
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/get_players', methods=['GET'])
def get_players():
    """Возвращает список игроков в сессии"""
    session_id = request.args.get('session_id', type=int)
    
    if not session_id:
        return jsonify({'error': 'Missing session_id'}), 400
    
    with session_lock:
        session_data = active_connections.get(session_id, {})
        players = []
        
        for user_id, player in session_data.get('players', {}).items():
            players.append({
                'user_id': user_id,
                'username': player.get('username'),
                'character_id': player.get('character_id'),
                'character_name': player.get('character_name'),
                'joined_at': player.get('joined_at')
            })
        
        gm = session_data.get('gm')
        
        return jsonify({
            'players': players,
            'gm_username': gm.get('username') if gm else None,
            'count': len(players)
        }), 200

@polling_bp.route('/ping', methods=['POST'])
def ping():
    """Обработчик пинга"""
    return jsonify({'status': 'ok'}), 200


def send_players_list(session_id):
    """Отправляет список игроков всем в сессии"""
    with session_lock:
        session_data = active_connections.get(session_id, {})
        players = []
        
        for user_id, player in session_data.get('players', {}).items():
            players.append({
                'user_id': user_id,
                'username': player.get('username'),
                'character_id': player.get('character_id'),
                'character_name': player.get('character_name')
            })
        
        gm = session_data.get('gm')
        
        queue = get_queue(session_id)
        queue.add_message({
            'type': 'players_list',
            'data': {
                'players': players,
                'gm_username': gm.get('username') if gm else None,
                'count': len(players)
            }
        })