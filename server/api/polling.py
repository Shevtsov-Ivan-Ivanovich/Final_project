# server/api/polling.py
from flask import Blueprint, request, jsonify
from datetime import datetime
import threading
from collections import deque

polling_bp = Blueprint('polling', __name__, url_prefix='/api/polling')

# Хранилище сообщений
class MessageQueue:
    def __init__(self, max_size=1000):
        self.messages = deque(maxlen=max_size)
        self.last_id = 0
        self.lock = threading.RLock()
    
    def add_message(self, message):
        with self.lock:
            self.last_id += 1
            message['id'] = self.last_id
            message['timestamp'] = datetime.now().isoformat()
            self.messages.append(message.copy())
            return self.last_id
    
    def get_messages(self, last_id=0):
        with self.lock:
            result = []
            for msg in self.messages:
                if msg['id'] > last_id:
                    result.append(msg.copy())
            return result

# Хранилища
session_queues = {}
session_lock = threading.RLock()
players_store = {}
gm_store = {}

def get_queue(session_id):
    with session_lock:
        if session_id not in session_queues:
            session_queues[session_id] = MessageQueue()
        return session_queues[session_id]

def send_players_list(session_id):
    """Отправляет список игроков всем в сессии"""
    with session_lock:
        players = []
        for user_id, player in players_store.get(session_id, {}).items():
            players.append({
                'user_id': user_id,
                'username': player.get('username'),
                'character_id': player.get('character_id'),
                'character_name': player.get('character_name')
            })
        
        gm = gm_store.get(session_id)
        
        queue = get_queue(session_id)
        queue.add_message({
            'type': 'players_list',
            'data': {
                'players': players,
                'gm_username': gm.get('username') if gm else None,
                'count': len(players)
            }
        })

@polling_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/register_gm', methods=['POST'])
def register_gm():
    data = request.json
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    username = data.get('username')
    
    print(f"[POLLING] REGISTER GM: session={session_id}, user={user_id}, username={username}")
    
    with session_lock:
        gm_store[session_id] = {'user_id': user_id, 'username': username}
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/register_player', methods=['POST'])
def register_player():
    import traceback
    print("!!! REGISTER_PLAYER called", flush=True)
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data'}), 400
        
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        username = data.get('username')
        character_id = data.get('character_id')
        character_name = data.get('character_name')
        
        print(f"!!! Data: session={session_id}, user={user_id}, char={character_name}", flush=True)
        
        if not all([session_id, user_id, username, character_id, character_name]):
            return jsonify({'error': 'Missing fields'}), 400
        
        # Проверяем сессию в БД
        from server.models import Session
        session = Session.query.get(session_id)   # <-- определяем переменную session
        if not session:
            print(f"!!! Session {session_id} not found", flush=True)
            return jsonify({'error': 'Session not found'}), 404
        print("!!! Session exists", flush=True)
        
        # Регистрируем игрока в памяти
        with session_lock:
            if session_id not in players_store:
                players_store[session_id] = {}
            players_store[session_id][user_id] = {
                'user_id': user_id,
                'username': username,
                'character_id': character_id,
                'character_name': character_name
            }
        print("!!! Player stored", flush=True)
        
        # Отправляем сообщения
        queue = get_queue(session_id)
        queue.add_message({
            'type': 'player_joined',
            'data': {
                'user_id': user_id,
                'username': username,
                'character_name': character_name,
                'message': f'{character_name} присоединился к игре!'
            }
        })
        send_players_list(session_id)
        print("!!! Messages sent", flush=True)
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        print(f"!!! Exception: {e}", flush=True)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@polling_bp.route('/disconnect', methods=['POST'])
def disconnect():
    data = request.json
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    print(f"[POLLING] DISCONNECT: session={session_id}, user={user_id}")
    
    with session_lock:
        if session_id in players_store and user_id in players_store[session_id]:
            player = players_store[session_id].pop(user_id)
            try:
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
            except Exception as e:
                print(f"[SERVER] Error: {e}")
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/messages', methods=['GET'])
def get_messages():
    session_id = request.args.get('session_id', type=int)
    user_id = request.args.get('user_id', type=int)
    last_id = request.args.get('last_id', 0, type=int)
    
    if not session_id or not user_id:
        return jsonify([]), 200
    
    try:
        queue = get_queue(session_id)
        messages = queue.get_messages(last_id)
        return jsonify(messages), 200
    except Exception as e:
        print(f"[SERVER] Error getting messages: {e}")
        return jsonify([]), 200

@polling_bp.route('/send_chat', methods=['POST'])
def send_chat():
    data = request.json
    print(f"[CHAT] Received: {data}", flush=True)
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    message = data.get('message', '').strip()
    action_type = data.get('action_type', 'chat')
    
    if not all([session_id, user_id]) or not message:
        print(f"[CHAT] Missing fields: session={session_id}, user={user_id}, msg='{message}'", flush=True)
        return jsonify({'error': 'Missing fields'}), 400
    
    with session_lock:
        character_name = None
        
        # Проверяем ГМ
        if session_id in gm_store and gm_store[session_id].get('user_id') == user_id:
            character_name = 'GM'
        
        # Проверяем игроков
        if not character_name and session_id in players_store:
            player = players_store[session_id].get(user_id)
            if player:
                character_name = player.get('character_name')
        
        if not character_name:
            return jsonify({'error': 'User not in session'}), 400
    
    try:
        queue = get_queue(session_id)
        queue.add_message({
            'type': 'chat_message',
            'data': {
                'user_id': user_id,
                'character_name': character_name,
                'message': message,
                'action_type': action_type,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        })
    except Exception as e:
        print(f"[SERVER] Error sending chat: {e}")
    
    return jsonify({'status': 'ok'}), 200

@polling_bp.route('/get_players', methods=['GET'])
def get_players():
    session_id = request.args.get('session_id', type=int)
    
    if not session_id:
        return jsonify({'players': [], 'count': 0}), 200
    
    with session_lock:
        players = []
        for user_id, player in players_store.get(session_id, {}).items():
            players.append({
                'user_id': user_id,
                'username': player.get('username'),
                'character_id': player.get('character_id'),
                'character_name': player.get('character_name')
            })
        
        gm = gm_store.get(session_id)
        
        return jsonify({
            'players': players,
            'gm_username': gm.get('username') if gm else None,
            'count': len(players)
        }), 200

@polling_bp.route('/ping', methods=['POST'])
def ping():
    return jsonify({'status': 'ok'}), 200