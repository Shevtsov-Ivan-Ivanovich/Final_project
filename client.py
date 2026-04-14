# client.py
import sys
import os

# Добавляем путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем PyQt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Импортируем наши модули
from client.windows.login_window import LoginWindow


def main():
    """Запуск клиента"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Запускаем окно входа
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()