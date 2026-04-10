import sys
import os

# Добавляем родительскую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import app

if __name__ == '__main__':
    print("=" * 60)
    print("ДПЖ - Сервер (HTTP Polling)")
    print("=" * 60)
    print("\nСервер запущен!")
    print("Адрес: http://localhost:5000")
    print("Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)