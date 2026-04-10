# client.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# ============ FIX QT PLUGINS FOR WINDOWS ============
def fix_qt_plugins():
    """Исправляет путь к Qt плагинам для Windows"""
    if sys.platform != 'win32':
        return
    
    # Список возможных путей к плагинам Qt
    possible_paths = [
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
    ]
    
    # Добавляем пути из site-packages
    try:
        import site
        for site_packages in site.getsitepackages():
            possible_paths.append(os.path.join(site_packages, 'PyQt5', 'Qt5', 'plugins'))
            possible_paths.append(os.path.join(site_packages, 'PyQt5', 'plugins'))
    except:
        pass
    
    # Ищем существующий путь
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = path
            print(f"Qt plugins path set to: {path}")
            break
    
    # Устанавливаем платформу
    os.environ['QT_QPA_PLATFORM'] = 'windows'
    
    # Добавляем путь к библиотекам Qt в PATH
    qt_bin_path = os.path.dirname(os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', ''))
    if qt_bin_path and os.path.exists(qt_bin_path):
        os.environ['PATH'] = qt_bin_path + os.pathsep + os.environ.get('PATH', '')

# Вызываем функцию ДО импорта PyQt5
fix_qt_plugins()

# Теперь импортируем PyQt5
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Добавляем путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем стили
try:
    from client.styles import FULL_STYLE
except ImportError:
    FULL_STYLE = ""

from client.windows.login_window import LoginWindow


class ClientApplication:
    def __init__(self):
        self.app = None
        self.login_window = None
    
    def run(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        if FULL_STYLE:
            self.app.setStyleSheet(FULL_STYLE)
        
        self.login_window = LoginWindow()
        self.login_window.show()
        
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = ClientApplication()
    app.run()