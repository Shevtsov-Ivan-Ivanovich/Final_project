# client/socket_client.py
import sys
import requests
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from client.config_manager import config_manager

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class SocketClient(QObject):
    connected_signal = pyqtSignal()
    disconnected_signal = pyqtSignal()
    chat_signal = pyqtSignal(dict)
    players_list_signal = pyqtSignal(dict)
    character_updated_signal = pyqtSignal(dict)
    item_added_signal = pyqtSignal(dict)
    item_removed_signal = pyqtSignal(dict)
    game_object_added_signal = pyqtSignal(dict)
    player_joined_signal = pyqtSignal(dict)
    player_disconnected_signal = pyqtSignal(dict)
    gm_disconnected_signal = pyqtSignal()
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.base_url = config_manager.base_url
        self.session_id = None
        self.user_id = None
        self.character_id = None
        self.is_gm = False
        self.is_connected = False
        self.last_message_id = 0
        self.polling_active = False
        self.polling_thread = None
        
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self._send_ping)
        self.ping_timer.setInterval(30000)
        
        print(f"[SOCKET] Created, server: {self.base_url}")
    
    def reset(self):
        """Полностью сбрасывает состояние клиента"""
        print(f"[SOCKET] Resetting...")
        self.disconnect()
    
    def connect_gm(self, session_id: int, user_id: int, username: str) -> bool:
        """Подключение как ГМ"""
        print(f"[SOCKET] Connecting as GM: session={session_id}, user={user_id}")
        
        self.disconnect()
        
        self.session_id = session_id
        self.user_id = user_id
        self.is_gm = True
        
        try:
            response = requests.post(
                f"{self.base_url}/api/polling/register_gm",
                json={'session_id': session_id, 'user_id': user_id, 'username': username},
                timeout=5
            )
            
            if response.status_code == 200:
                self.is_connected = True
                self._start_polling()
                self.ping_timer.start()
                self.connected_signal.emit()
                print(f"[SOCKET] GM connected successfully")
                return True
            else:
                print(f"[SOCKET] GM connection failed: {response.text}")
                return False
        except Exception as e:
            print(f"[SOCKET] GM connection error: {e}")
            return False
    
    def connect_player(self, session_id: int, user_id: int, username: str, 
                    character_id: int, character_name: str) -> bool:
        """Подключение как игрок"""
        print(f"[SOCKET] === CONNECT_PLAYER CALLED ===")
        print(f"[SOCKET] URL: {self.base_url}/api/polling/register_player")
        print(f"[SOCKET] Data: session_id={session_id}, user_id={user_id}, username={username}, character_id={character_id}, character_name={character_name}")
        
        self.disconnect()
        
        self.session_id = session_id
        self.user_id = user_id
        self.character_id = character_id
        self.is_gm = False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/polling/register_player",
                json={
                    'session_id': session_id,
                    'user_id': user_id,
                    'username': username,
                    'character_id': character_id,
                    'character_name': character_name
                },
                timeout=30
            )
            
            print(f"[SOCKET] Response status: {response.status_code}")
            print(f"[SOCKET] Response text: {response.text}")
            
            if response.status_code == 200:
                self.is_connected = True
                self._start_polling()
                self.ping_timer.start()
                self.connected_signal.emit()
                print(f"[SOCKET] Player connected successfully")
                return True
            else:
                print(f"[SOCKET] Player connection failed")
                return False
        except Exception as e:
            print(f"[SOCKET] Player connection error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def disconnect(self):
        """Отключение от сессии"""
        print(f"[SOCKET] Disconnecting...")
        
        self.polling_active = False
        self.ping_timer.stop()
        
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2)
        
        if self.session_id and self.user_id and self.is_connected:
            try:
                requests.post(
                    f"{self.base_url}/api/polling/disconnect",
                    json={'session_id': self.session_id, 'user_id': self.user_id},
                    timeout=2
                )
            except:
                pass
        
        self.session_id = None
        self.user_id = None
        self.character_id = None
        self.is_gm = False
        self.is_connected = False
        self.last_message_id = 0
        self.polling_thread = None
        
        self.disconnected_signal.emit()
        print(f"[SOCKET] Disconnected")
    
    def _start_polling(self):
        """Запуск polling потока"""
        self.polling_active = True
        self.last_message_id = 0
        self.polling_thread = threading.Thread(target=self._poll_messages, daemon=True)
        self.polling_thread.start()
        print(f"[SOCKET] Polling started")
    
    def _poll_messages(self):
        """Polling сообщений"""
        empty_count = 0
        
        while self.polling_active and self.session_id and self.user_id:
            try:
                response = requests.get(
                    f"{self.base_url}/api/polling/messages",
                    params={
                        'session_id': self.session_id,
                        'user_id': self.user_id,
                        'last_id': self.last_message_id
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    messages = response.json()
                    
                    if messages:
                        for msg in messages:
                            self._process_message(msg)
                            self.last_message_id = msg['id']
                        empty_count = 0
                        time.sleep(0.5)
                    else:
                        empty_count += 1
                        wait = min(empty_count * 0.5, 5)
                        time.sleep(wait)
                        
            except requests.Timeout:
                continue
            except Exception as e:
                print(f"[SOCKET] Polling error: {e}")
                time.sleep(5)
        
        print(f"[SOCKET] Polling stopped")
    
    def _process_message(self, message: dict):
        """Обработка сообщения"""
        msg_type = message.get('type')
        data = message.get('data', {})
        
        handlers = {
            'chat_message': self.chat_signal,
            'players_list': self.players_list_signal,
            'character_updated': self.character_updated_signal,
            'item_added': self.item_added_signal,
            'item_removed': self.item_removed_signal,
            'game_object_added': self.game_object_added_signal,
            'player_joined': self.player_joined_signal,
            'player_disconnected': self.player_disconnected_signal,
            'gm_disconnected': self.gm_disconnected_signal,
        }
        
        if msg_type in handlers:
            handlers[msg_type].emit(data)
    
    def _send_ping(self):
        """Отправка ping"""
        if self.is_connected and self.session_id and self.user_id:
            try:
                requests.post(
                    f"{self.base_url}/api/polling/ping",
                    json={'session_id': self.session_id, 'user_id': self.user_id},
                    timeout=2
                )
            except:
                pass
    
    def send_chat(self, message: str, action_type: str = 'chat'):
        """Отправка сообщения в чат"""
        if not self.is_connected:
            return
        
        try:
            requests.post(
                f"{self.base_url}/api/polling/send_chat",
                json={
                    'session_id': self.session_id,
                    'user_id': self.user_id,
                    'message': message,
                    'action_type': action_type
                },
                timeout=5
            )
        except Exception as e:
            print(f"[SOCKET] Send error: {e}")
    
    def get_players(self):
        """Получение списка игроков"""
        if not self.session_id:
            return
        
        try:
            response = requests.get(
                f"{self.base_url}/api/polling/get_players",
                params={'session_id': self.session_id},
                timeout=5
            )
            
            if response.status_code == 200:
                self.players_list_signal.emit(response.json())
        except Exception as e:
            print(f"[SOCKET] Get players error: {e}")