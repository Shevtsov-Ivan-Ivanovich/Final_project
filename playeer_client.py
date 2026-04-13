# playeer_client.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from client.windows.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Проверяем подключение к серверу (без запуска)
    from client.config_manager import config_manager
    success, msg = config_manager.test_connection()
    
    if not success:
        print(f"[WARN] Server not available: {msg}")
        print(f"[INFO] Please check server connection in settings")
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()