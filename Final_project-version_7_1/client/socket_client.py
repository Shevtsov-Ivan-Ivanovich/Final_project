# client/socket_client.py
import requests
import threading
import time
import json
import os
from typing import Optional, Dict, Any, Callable
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime


class SocketClient(QObject):
    """HTTP Long Polling клиент вместо WebSocket"""
    
    # Сигналы для обновления UI
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
        self.base_url = "http://localhost:5000"
        self.is_connected = False
        self.current_session_id = None
        self.current_user_id = None
        self.current_character_id = None
        self.is_gm = False
        self.server_ip = "localhost"
        self.server_port = 5000
        
        self.polling_thread = None
        self.is_polling = False
        self.last_message_id = 0
        
        # Таймер для пинга
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self.send_ping)
        self.ping_timer.setInterval(30000)  # Каждые 30 секунд
        
        self.load_server_config()
    
    def load_server_config(self):
        """Загружает настройки сервера из конфига"""
        config_file = "client_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_url = config.get('api_url', 'http://127.0.0.1:5000/api')
                    url_part = api_url.replace('http://', '').replace('/api', '')
                    if ':' in url_part:
                        ip, port = url_part.split(':')
                        self.server_ip = ip
                        self.server_port = int(port)
                    else:
                        self.server_ip = url_part
                        self.server_port = 5000
                    self.base_url = f"http://{self.server_ip}:{self.server_port}"
                    print(f"Loaded server config: {self.base_url}")
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def connect_to_server(self, server_ip: str = None, port: int = None):
        """Подключается к серверу"""
        if server_ip:
            self.server_ip = server_ip
        if port:
            self.server_port = port
        self.base_url = f"http://{self.server_ip}:{self.server_port}"
        
        try:
            # Используем 127.0.0.1 вместо localhost
            test_url = f"http://127.0.0.1:{self.server_port}/api/health"
            print(f"🔌 Connecting to {test_url}...")
            
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                self.base_url = f"http://127.0.0.1:{self.server_port}"
                self.is_connected = True
                self.connected_signal.emit()
                print(f"✅ Connected to server at {self.base_url}")
                return True
            else:
                self.error_signal.emit(f"Сервер вернул ошибку: {response.status_code}")
                return False
        except Exception as e:
            print(f"Connection error: {e}")
            self.error_signal.emit(f"Ошибка подключения: {e}")
            return False
 
    def disconnect(self):
        """Отключается от сервера"""
        self.is_polling = False
        self.ping_timer.stop()
        
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(timeout=2)
        
        # Отправляем уведомление об отключении
        if self.current_session_id and self.current_user_id:
            try:
                requests.post(f"{self.base_url}/api/polling/disconnect", json={
                    'session_id': self.current_session_id,
                    'user_id': self.current_user_id
                }, timeout=2)
            except:
                pass
        
        self.current_session_id = None
        self.current_user_id = None
        self.current_character_id = None
        self.is_connected = False
        self.disconnected_signal.emit()
    
    def register_gm(self, session_id: int, user_id: int, username: str):
        """Регистрирует ГМ в сессии"""
        self.current_session_id = session_id
        self.current_user_id = user_id
        self.is_gm = True
        
        try:
            response = requests.post(f"{self.base_url}/api/polling/register_gm", json={
                'session_id': session_id,
                'user_id': user_id,
                'username': username
            }, timeout=10)
            
            if response.status_code == 200:
                self.is_connected = True
                self.ping_timer.start()
                self.start_polling()
                print(f"🎮 Registered as GM in session {session_id}")
                return True
            else:
                self.error_signal.emit(f"Ошибка регистрации GM: {response.text}")
                return False
        except Exception as e:
            print(f"Register GM error: {e}")
            self.error_signal.emit(f"Ошибка регистрации GM: {e}")
            return False
    
    def register_player(self, session_id: int, user_id: int, username: str, 
                        character_id: int, character_name: str):
        """Регистрирует игрока в сессии"""
        self.current_session_id = session_id
        self.current_user_id = user_id
        self.current_character_id = character_id
        self.is_gm = False
        
        try:
            response = requests.post(f"{self.base_url}/api/polling/register_player", json={
                'session_id': session_id,
                'user_id': user_id,
                'username': username,
                'character_id': character_id,
                'character_name': character_name
            }, timeout=10)
            
            if response.status_code == 200:
                self.is_connected = True
                self.ping_timer.start()
                self.start_polling()
                print(f"🎮 Registered as player {character_name} in session {session_id}")
                return True
            else:
                self.error_signal.emit(f"Ошибка регистрации игрока: {response.text}")
                return False
        except Exception as e:
            print(f"Register player error: {e}")
            self.error_signal.emit(f"Ошибка регистрации игрока: {e}")
            return False
    
    def start_polling(self):
        """Запускает polling для получения сообщений"""
        self.is_polling = True
        self.last_message_id = 0
        self.polling_thread = threading.Thread(target=self._poll_messages, daemon=True)
        self.polling_thread.start()
    
    def _poll_messages(self):
        """Polling цикл для получения сообщений от сервера"""
        while self.is_polling and self.current_session_id and self.current_user_id:
            try:
                response = requests.get(
                    f"{self.base_url}/api/polling/messages",
                    params={
                        'session_id': self.current_session_id,
                        'user_id': self.current_user_id,
                        'last_id': self.last_message_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    messages = response.json()
                    for msg in messages:
                        self._process_message(msg)
                        self.last_message_id = msg['id']
                elif response.status_code == 504:
                    # Timeout - нормально, продолжаем
                    pass
                else:
                    print(f"Polling error: {response.status_code}")
                    time.sleep(2)
                    
            except requests.Timeout:
                # Таймаут ожидания - нормально
                continue
            except Exception as e:
                print(f"Polling exception: {e}")
                time.sleep(5)
    
    def _process_message(self, message: dict):
        """Обрабатывает полученное сообщение"""
        msg_type = message.get('type')
        data = message.get('data', {})
        
        if msg_type == 'chat_message':
            self.chat_signal.emit(data)
        elif msg_type == 'players_list':
            self.players_list_signal.emit(data)
        elif msg_type == 'character_updated':
            self.character_updated_signal.emit(data)
        elif msg_type == 'item_added':
            self.item_added_signal.emit(data)
        elif msg_type == 'item_removed':
            self.item_removed_signal.emit(data)
        elif msg_type == 'game_object_added':
            self.game_object_added_signal.emit(data)
        elif msg_type == 'player_joined':
            self.player_joined_signal.emit(data)
        elif msg_type == 'player_disconnected':
            self.player_disconnected_signal.emit(data)
        elif msg_type == 'gm_disconnected':
            self.gm_disconnected_signal.emit()
        elif msg_type == 'error':
            self.error_signal.emit(data.get('message', 'Unknown error'))
    
    def send_ping(self):
        """Отправляет пинг серверу"""
        if self.current_session_id and self.current_user_id:
            try:
                requests.post(f"{self.base_url}/api/polling/ping", json={
                    'session_id': self.current_session_id,
                    'user_id': self.current_user_id,
                    'timestamp': int(time.time() * 1000)
                }, timeout=5)
            except Exception as e:
                print(f"Ping error: {e}")
    
    def send_chat(self, message: str, action_type: str = 'chat'):
        """Отправляет сообщение в чат"""
        if not self.current_session_id or not self.current_user_id:
            self.error_signal.emit("Не подключен к сессии")
            return
        
        try:
            response = requests.post(f"{self.base_url}/api/polling/send_chat", json={
                'session_id': self.current_session_id,
                'user_id': self.current_user_id,
                'message': message,
                'action_type': action_type
            }, timeout=10)
            
            if response.status_code != 200:
                self.error_signal.emit(f"Ошибка отправки: {response.text}")
        except Exception as e:
            print(f"Send chat error: {e}")
            self.error_signal.emit(f"Ошибка отправки: {e}")
    
    def gm_update_character(self, character_id: int, updates: Dict):
        """ГМ обновляет характеристики персонажа"""
        if not self.is_gm:
            return
        
        try:
            requests.post(f"{self.base_url}/api/polling/gm_update_character", json={
                'session_id': self.current_session_id,
                'character_id': character_id,
                'updates': updates
            }, timeout=10)
        except Exception as e:
            print(f"Update character error: {e}")
    
    def gm_add_item(self, character_id: int, item_id: int, quantity: int = 1):
        """ГМ добавляет предмет персонажу"""
        if not self.is_gm:
            return
        
        try:
            requests.post(f"{self.base_url}/api/polling/gm_add_item", json={
                'session_id': self.current_session_id,
                'character_id': character_id,
                'item_id': item_id,
                'quantity': quantity
            }, timeout=10)
        except Exception as e:
            print(f"Add item error: {e}")
    
    def gm_remove_item(self, character_id: int, item_id: int):
        """ГМ удаляет предмет у персонажа"""
        if not self.is_gm:
            return
        
        try:
            requests.post(f"{self.base_url}/api/polling/gm_remove_item", json={
                'session_id': self.current_session_id,
                'character_id': character_id,
                'item_id': item_id
            }, timeout=10)
        except Exception as e:
            print(f"Remove item error: {e}")
    
    def add_game_object(self, obj_type: str, name: str, description: str = "", data: Dict = None):
        """Добавляет игровой объект"""
        if not self.is_gm:
            return
        
        try:
            requests.post(f"{self.base_url}/api/polling/add_game_object", json={
                'session_id': self.current_session_id,
                'type': obj_type,
                'name': name,
                'description': description,
                'data': data or {}
            }, timeout=10)
        except Exception as e:
            print(f"Add game object error: {e}")
    
    def get_players(self):
        """Запрашивает список игроков"""
        if not self.current_session_id:
            return
        
        try:
            response = requests.get(f"{self.base_url}/api/polling/get_players", params={
                'session_id': self.current_session_id
            }, timeout=10)
            
            if response.status_code == 200:
                self.players_list_signal.emit(response.json())
        except Exception as e:
            print(f"Get players error: {e}")


socket_client = SocketClient()