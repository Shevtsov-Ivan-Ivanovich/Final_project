# client/api_client.py
import requests
from typing import Optional, Dict, List, Any
from client.config_manager import config_manager

class APIClient:
    """API клиент для работы с сервером"""
    
    def __init__(self):
        self.base_url = config_manager.api_url
        self._ensure_server_config()
    
    def _ensure_server_config(self):
        """Проверяет конфигурацию сервера"""
        success, msg = config_manager.test_connection()
        if not success:
            print(f"[API] Server not available: {msg}")
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Универсальный метод для запросов"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, timeout=10)
            else:
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"[API] Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"[API] Request error: {e}")
            return None
    
    # Auth
    def login(self, login_or_email: str, password: str) -> Optional[Dict]:
        result = self._request("POST", "/auth/login", {
            'login_or_email': login_or_email,
            'password': password
        })
        return result.get('user') if result else None
    
    def register(self, username: str, email: str, password: str) -> Optional[Dict]:
        result = self._request("POST", "/auth/register", {
            'username': username,
            'email': email,
            'password': password
        })
        return result.get('user') if result else None
    
    # Characters
    def get_my_characters(self, user_id: int) -> List[Dict]:
        result = self._request("GET", f"/characters/my/{user_id}")
        return result if isinstance(result, list) else []
    
    def create_character(self, user_id: int, name: str) -> Optional[Dict]:
        result = self._request("POST", "/characters/", {
            'user_id': user_id,
            'name': name
        })
        return result.get('character') if result else None
    
    def delete_character(self, character_id: int) -> bool:
        result = self._request("DELETE", f"/characters/{character_id}")
        return result is not None and result.get('success', False)
    
    def update_character(self, character_id: int, updates: Dict) -> bool:
        result = self._request("PUT", f"/characters/{character_id}", updates)
        return result is not None and result.get('success', False)
    
    def get_character_inventory(self, character_id: int) -> List[Dict]:
        result = self._request("GET", f"/characters/{character_id}/inventory")
        return result if isinstance(result, list) else []
    
    def add_item_to_character(self, character_id: int, item_id: int, quantity: int = 1) -> bool:
        result = self._request("POST", f"/characters/{character_id}/add_item", {
            'item_id': item_id,
            'quantity': quantity
        })
        return result is not None and result.get('success', False)
    
    def remove_item_from_character(self, character_id: int, item_id: int) -> bool:
        result = self._request("DELETE", f"/characters/{character_id}/remove_item/{item_id}")
        return result is not None and result.get('success', False)
    
    def equip_item(self, character_id: int, item_id: int) -> bool:
        result = self._request("POST", f"/characters/{character_id}/equip/{item_id}")
        return result is not None and result.get('success', False)
    
    def unequip_item(self, character_id: int, item_id: int) -> bool:
        result = self._request("POST", f"/characters/{character_id}/unequip/{item_id}")
        return result is not None and result.get('success', False)
    
    def attach_character_to_session(self, character_id: int, session_id: int) -> bool:
        result = self._request("POST", "/characters/attach_to_session", {
            'character_id': character_id,
            'session_id': session_id
        })
        return result is not None and result.get('success', False)
    
    def detach_character_from_session(self, character_id: int) -> bool:
        result = self._request("POST", "/characters/detach_from_session", {
            'character_id': character_id
        })
        return result is not None and result.get('success', False)
    
    # Sessions
    def get_all_sessions(self) -> List[Dict]:
        result = self._request("GET", "/sessions/")
        return result if isinstance(result, list) else []
    
    def get_my_sessions(self, user_id: int) -> List[Dict]:
        result = self._request("GET", f"/sessions/my/{user_id}")
        return result if isinstance(result, list) else []
    
    def create_session(self, name: str, master_id: int, description: str = "") -> Optional[Dict]:
        result = self._request("POST", "/sessions/", {
            'name': name,
            'master_id': master_id,
            'description': description
        })
        return result.get('session') if result else None
    
    def delete_session(self, session_id: int) -> bool:
        result = self._request("DELETE", f"/sessions/{session_id}")
        return result is not None and result.get('success', False)
    
    def join_session(self, session_id: int, user_id: int) -> bool:
        result = self._request("POST", f"/sessions/{session_id}/join", {
            'user_id': user_id
        })
        return result is not None and result.get('success', False)
    
    def leave_session(self, session_id: int, user_id: int) -> bool:
        result = self._request("POST", f"/sessions/{session_id}/leave", {
            'user_id': user_id
        })
        return result is not None and result.get('success', False)
    
    def get_session_participants(self, session_id: int) -> List[Dict]:
        result = self._request("GET", f"/sessions/{session_id}/participants")
        return result.get('participants', []) if result else []
    
    # Items
    def get_all_items(self) -> List[Dict]:
        result = self._request("GET", "/items/")
        return result if isinstance(result, list) else []
    
    def create_item(self, name: str, **kwargs) -> Optional[Dict]:
        data = {'name': name, **kwargs}
        result = self._request("POST", "/items/", data)
        return result.get('item') if result else None
    
    def delete_item(self, item_id: int) -> bool:
        result = self._request("DELETE", f"/items/{item_id}")
        return result is not None and result.get('success', False)
    
    # Game Contexts
    def get_session_contexts(self, session_id: int) -> List[Dict]:
        result = self._request("GET", f"/game_contexts/session/{session_id}")
        return result if isinstance(result, list) else []
    
    def create_context(self, session_id: int, context_type: str, name: str, 
                       description: str = "", data: Dict = None) -> Optional[Dict]:
        result = self._request("POST", "/game_contexts/", {
            'session_id': session_id,
            'context_type': context_type,
            'name': name,
            'description': description,
            'data': data or {}
        })
        return result.get('context') if result else None
    
    def delete_context(self, context_id: int) -> bool:
        result = self._request("DELETE", f"/game_contexts/{context_id}")
        return result is not None and result.get('success', False)
    
    # Logs
    def get_session_logs(self, session_id: int) -> List[Dict]:
        result = self._request("GET", f"/logs/session/{session_id}")
        return result if isinstance(result, list) else []
    def get_session_by_id(self, session_id: int) -> Optional[Dict]:
        """Получает сессию по ID"""
        sessions = self.get_all_sessions()
        for session in sessions:
            if session['id'] == session_id:
                return session
        return None
    
    def update_character_session(self, character_id: int, session_id: int) -> bool:
        """Обновляет привязку персонажа к сессии"""
        result = self._request("PUT", f"/characters/{character_id}", {
            'session_id': session_id
        })
        return result is not None and result.get('success', False)    

# Глобальный экземпляр
api_client = APIClient()