# server/config.py
import os
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    # Используем SQLite для простоты
    SQLALCHEMY_DATABASE_URI = 'sqlite:///game.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки CORS
    CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000", "http://192.168.10.163:5000"]
    CORS_ALLOW_ALL_ORIGINS = True 