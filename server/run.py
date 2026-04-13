# server/run.py
import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import app

if __name__ == '__main__':
    print("=" * 60)
    print("DPJ - Server (HTTP Polling)")
    print("=" * 60)
    print("\nServer started!")
    print("Address: http://localhost:5000")
    print("=" * 60)
    
    # Выводим все маршруты для отладки
    print("\n[ROUTES] Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"   {methods:10} {rule.rule}")
    
    print("\n" + "=" * 60)
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=False)