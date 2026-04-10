# client/api_client.py
import json
import os
import requests
from typing import Optional, Dict, Any, List

from client.network_config import network_config


class APIClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or network_config.get_api_url()
        self.load_server_config()

    def load_server_config(self):
        """Загружает настройки сервера из конфига"""
        config_file = os.path.join(os.path.dirname(__file__), "client_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_url = config.get('api_url', 'http://127.0.0.1:5000/api')
                    self.base_url = api_url
                    print(f"Loaded API config: {self.base_url}")
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def set_server(self, ip: str, port: int = 5000):
        self.base_url = f"http://{ip}:{port}/api"
        network_config.save_config(ip, port)
    
    # Auth
    def login(self, login_or_email: str, password: str) -> Optional[Dict]:
        try:
            response = requests.post(f"{self.base_url}/auth/login", json={
                'login_or_email': login_or_email,
                'password': password
            }, timeout=10)
            if response.status_code == 200:
                return response.json().get('user')
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def register(self, username: str, email: str, password: str) -> Optional[Dict]:
        try:
            response = requests.post(f"{self.base_url}/auth/register", json={
                'username': username,
                'email': email,
                'password': password
            }, timeout=10)
            if response.status_code == 200:
                return response.json().get('user')
            return None
        except Exception as e:
            print(f"Register error: {e}")
            return None
    
    # Characters
    def get_my_characters(self, user_id: int) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/characters/my/{user_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get characters error: {e}")
            return []
    
    def create_character(self, user_id: int, name: str, **stats) -> Optional[Dict]:
        try:
            data = {
                'user_id': user_id,
                'name': name,
                **stats
            }
            response = requests.post(f"{self.base_url}/characters/", json=data, timeout=10)
            if response.status_code == 201:
                return response.json().get('character')
            return None
        except Exception as e:
            print(f"Create character error: {e}")
            return None
    
    def delete_character(self, character_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/characters/{character_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Delete character error: {e}")
            return False
    
    def update_character(self, character_id: int, updates: Dict) -> bool:
        try:
            response = requests.put(f"{self.base_url}/characters/{character_id}", json=updates, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Update character error: {e}")
            return False
    
    def get_character_inventory(self, character_id: int) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/characters/{character_id}/inventory", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get inventory error: {e}")
            return []
    
    def add_item_to_character(self, character_id: int, item_id: int, quantity: int = 1) -> bool:
        try:
            response = requests.post(f"{self.base_url}/characters/{character_id}/add_item", 
                                    json={'item_id': item_id, 'quantity': quantity}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Add item error: {e}")
            return False
    
    def remove_item_from_character(self, character_id: int, item_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/characters/{character_id}/remove_item/{item_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Remove item error: {e}")
            return False
    
    def equip_item(self, character_id: int, item_id: int) -> bool:
        """Экипировать предмет"""
        try:
            response = requests.post(f"{self.base_url}/characters/{character_id}/equip/{item_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Equip item error: {e}")
            return False
    
    def unequip_item(self, character_id: int, item_id: int) -> bool:
        """Снять экипировку"""
        try:
            response = requests.post(f"{self.base_url}/characters/{character_id}/unequip/{item_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Unequip item error: {e}")
            return False
    
    def attach_character_to_session(self, character_id: int, session_id: int) -> bool:
        try:
            response = requests.post(f"{self.base_url}/characters/attach_to_session",
                                    json={'character_id': character_id, 'session_id': session_id}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Attach character error: {e}")
            return False
    
    def detach_character_from_session(self, character_id: int) -> bool:
        try:
            response = requests.post(f"{self.base_url}/characters/detach_from_session",
                                    json={'character_id': character_id}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Detach character error: {e}")
            return False
    
    # Sessions
    def get_all_sessions(self) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/sessions/", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get sessions error: {e}")
            return []
    
    def get_my_sessions(self, user_id: int) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/sessions/my/{user_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get my sessions error: {e}")
            return []
    
    def get_available_sessions(self, user_id: int) -> List[Dict]:
        """Получить доступные сессии (в которых пользователь не участвует)"""
        try:
            response = requests.get(f"{self.base_url}/sessions/available/{user_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get available sessions error: {e}")
            return []
    
    def create_session(self, name: str, master_id: int, description: str = "") -> Optional[Dict]:
        try:
            response = requests.post(f"{self.base_url}/sessions/", json={
                'name': name,
                'master_id': master_id,
                'description': description
            }, timeout=10)
            if response.status_code == 201:
                return response.json().get('session')
            return None
        except Exception as e:
            print(f"Create session error: {e}")
            return None
    
    def delete_session(self, session_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/sessions/{session_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Delete session error: {e}")
            return False
    
    def join_session(self, session_id: int, user_id: int) -> bool:
        try:
            response = requests.post(f"{self.base_url}/sessions/{session_id}/join",
                                    json={'user_id': user_id}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Join session error: {e}")
            return False
    
    def leave_session(self, session_id: int, user_id: int) -> bool:
        try:
            response = requests.post(f"{self.base_url}/sessions/{session_id}/leave",
                                    json={'user_id': user_id}, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Leave session error: {e}")
            return False
    
    def get_session_participants(self, session_id: int) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/sessions/{session_id}/participants", timeout=10)
            if response.status_code == 200:
                return response.json().get('participants', [])
            return []
        except Exception as e:
            print(f"Get participants error: {e}")
            return []
    
    # Items
    def get_all_items(self) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/items/", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get items error: {e}")
            return []
    
    def create_item(self, name: str, **kwargs) -> Optional[Dict]:
        try:
            data = {'name': name, **kwargs}
            response = requests.post(f"{self.base_url}/items/", json=data, timeout=10)
            if response.status_code == 201:
                return response.json().get('item')
            return None
        except Exception as e:
            print(f"Create item error: {e}")
            return None
    
    def delete_item(self, item_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/items/{item_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Delete item error: {e}")
            return False
    
    # Game Contexts
    def get_session_contexts(self, session_id: int) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/game_contexts/session/{session_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get contexts error: {e}")
            return []
    
    def create_context(self, session_id: int, context_type: str, name: str, description: str = "", data: Dict = None) -> Optional[Dict]:
        try:
            response = requests.post(f"{self.base_url}/game_contexts/", json={
                'session_id': session_id,
                'context_type': context_type,
                'name': name,
                'description': description,
                'data': data or {}
            }, timeout=10)
            if response.status_code == 201:
                return response.json().get('context')
            return None
        except Exception as e:
            print(f"Create context error: {e}")
            return None
    
    def delete_context(self, context_id: int) -> bool:
        try:
            response = requests.delete(f"{self.base_url}/game_contexts/{context_id}", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Delete context error: {e}")
            return False
    
    # Logs
    def create_log(self, action_type: str, performer_id: int, **kwargs) -> bool:
        try:
            data = {
                'action_type': action_type,
                'performer_id': performer_id,
                **kwargs
            }
            response = requests.post(f"{self.base_url}/logs/", json=data, timeout=10)
            return response.status_code == 201
        except Exception as e:
            print(f"Create log error: {e}")
            return False
    
    def get_session_logs(self, session_id: int) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/logs/session/{session_id}", timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Get logs error: {e}")
            return []


api_client = APIClient()