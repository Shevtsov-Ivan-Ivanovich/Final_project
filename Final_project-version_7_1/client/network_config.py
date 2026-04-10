# client/network_config.py
"""
Файл конфигурации сети для клиента ДПЖ
Все настройки подключения к серверу хранятся здесь для удобства замены
"""

import json
import os

class NetworkConfig:
    """Конфигурация сетевых параметров"""
    
    # Значения по умолчанию
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 5000
    DEFAULT_API_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}/api"
    
    def __init__(self):
        self.host = self.DEFAULT_HOST
        self.port = self.DEFAULT_PORT
        self.api_url = self.DEFAULT_API_URL
        self.load_config()
    
    def load_config(self):
        """Загружает конфигурацию из файла"""
        config_file = os.path.join(os.path.dirname(__file__), "client_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_url = config.get('api_url', self.DEFAULT_API_URL)
                    self.api_url = api_url
                    
                    # Парсим host и port из URL
                    url_part = api_url.replace('http://', '').replace('/api', '')
                    if ':' in url_part:
                        self.host, port_str = url_part.split(':')
                        self.port = int(port_str)
                    else:
                        self.host = url_part
                        self.port = self.DEFAULT_PORT
                    print(f"Loaded network config: {self.host}:{self.port}")
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self, host: str = None, port: int = None, api_url: str = None):
        """Сохраняет конфигурацию в файл"""
        if api_url:
            self.api_url = api_url
        elif host and port:
            self.api_url = f"http://{host}:{port}/api"
            self.host = host
            self.port = port
        else:
            return
        
        config_file = os.path.join(os.path.dirname(__file__), "client_config.json")
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'api_url': self.api_url}, f, indent=2)
            print(f"Saved network config: {self.api_url}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_base_url(self) -> str:
        """Возвращает базовый URL сервера (без /api)"""
        return f"http://{self.host}:{self.port}"
    
    def get_api_url(self) -> str:
        """Возвращает API URL"""
        return self.api_url


# Создаем глобальный экземпляр конфигурации
network_config = NetworkConfig()