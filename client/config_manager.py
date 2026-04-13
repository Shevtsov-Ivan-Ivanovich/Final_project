# client/config_manager.py
import json
import os
from pathlib import Path

class ConfigManager:
    """Централизованное управление конфигурацией"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _get_config_path(self):
        """Получает путь к файлу конфигурации"""
        # Ищем config.json в разных местах
        possible_paths = [
            Path(__file__).parent.parent / "config.json",  # Корень проекта
            Path(__file__).parent / "config.json",         # Папка client
            Path.cwd() / "config.json",                    # Текущая рабочая директория
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Если нет - создаем в корне проекта
        default_path = Path(__file__).parent.parent / "config.json"
        self._create_default_config(default_path)
        return default_path
    
    def _create_default_config(self, path):
        """Создает конфиг по умолчанию"""
        default_config = {
            "server": {
                "host": "127.0.0.1",
                "port": 5000,
                "api_url": "http://127.0.0.1:5000/api"
            },
            "debug": True
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"[CONFIG] Created default config at {path}")
    
    def _load_config(self):
        """Загружает конфигурацию"""
        try:
            config_path = self._get_config_path()
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[CONFIG] Loaded from {config_path}")
            return config
        except Exception as e:
            print(f"[CONFIG] Error loading: {e}")
            return {
                "server": {
                    "host": "127.0.0.1",
                    "port": 5000,
                    "api_url": "http://127.0.0.1:5000/api"
                },
                "debug": True
            }
    
    def save_config(self):
        """Сохраняет текущую конфигурацию"""
        try:
            config_path = self._get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            print(f"[CONFIG] Saved to {config_path}")
            return True
        except Exception as e:
            print(f"[CONFIG] Error saving: {e}")
            return False
    
    @property
    def host(self):
        return self._config.get("server", {}).get("host", "127.0.0.1")
    
    @property
    def port(self):
        return self._config.get("server", {}).get("port", 5000)
    
    @property
    def api_url(self):
        return self._config.get("server", {}).get("api_url", f"http://{self.host}:{self.port}/api")
    
    @property
    def base_url(self):
        return f"http://{self.host}:{self.port}"
    
    def update_server(self, host=None, port=None):
        """Обновляет настройки сервера"""
        if host:
            self._config["server"]["host"] = host
        if port:
            self._config["server"]["port"] = port
        
        self._config["server"]["api_url"] = f"http://{self.host}:{self.port}/api"
        self.save_config()
    
    def test_connection(self, host=None, port=None):
        """Тестирует подключение к серверу"""
        import requests
        
        test_host = host or self.host
        test_port = port or self.port
        test_url = f"http://{test_host}:{test_port}/api/health"
        
        try:
            response = requests.get(test_url, timeout=3)
            if response.status_code == 200:
                return True, "OK"
            return False, f"HTTP {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Сервер не отвечает"
        except requests.exceptions.Timeout:
            return False, "Таймаут подключения"
        except Exception as e:
            return False, str(e)

# Глобальный экземпляр
config_manager = ConfigManager()