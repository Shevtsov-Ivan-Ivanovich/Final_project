# quick_test.py
import requests

print("Testing health...")
r = requests.get("http://127.0.0.1:5000/api/health")
print(f"Health: {r.status_code} - {r.json()}")

print("\nTesting register_player...")
data = {
    'session_id': 1,
    'user_id': 1,
    'username': 'admin',
    'character_id': 1,
    'character_name': 'TestChar'
}
try:
    r = requests.post("http://127.0.0.1:5000/api/polling/register_player", json=data, timeout=5)
    print(f"Register: {r.status_code} - {r.text}")
except Exception as e:
    print(f"Error: {e}")