# test_client_connection.py
import sys
import os

# Добавляем путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.api_client import api_client
from client.socket_client import socket_client

print("=" * 50)
print("Тест подключения к серверу")
print("=" * 50)

# Тест API
print("\n1. Тест API подключения:")
try:
    # Проверяем health
    import requests
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"   ✅ API работает: {response.json()}")
except Exception as e:
    print(f"   ❌ API ошибка: {e}")

# Тест WebSocket
print("\n2. Тест WebSocket подключения:")
try:
    socket_client.connect_to_server("localhost", 5000)
    import time
    time.sleep(2)
    if socket_client.is_connected:
        print(f"   ✅ WebSocket подключен!")
        socket_client.disconnect()
    else:
        print(f"   ❌ WebSocket не подключен")
except Exception as e:
    print(f"   ❌ WebSocket ошибка: {e}")

print("\n" + "=" * 50)
