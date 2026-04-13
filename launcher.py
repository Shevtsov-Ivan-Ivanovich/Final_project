# launcher.py
import sys
import os
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# ============ FIX QT PLUGINS FOR WINDOWS ============
def fix_qt_plugins():
    """Исправляет путь к Qt плагинам для Windows"""
    if sys.platform != 'win32':
        return
    
    possible_paths = [
        os.path.join(sys.prefix, 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
        os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'PyQt5', 'Qt5', 'plugins'),
    ]
    
    try:
        import site
        for site_packages in site.getsitepackages():
            possible_paths.append(os.path.join(site_packages, 'PyQt5', 'Qt5', 'plugins'))
            possible_paths.append(os.path.join(site_packages, 'PyQt5', 'plugins'))
    except:
        pass
    
    try:
        import PyQt5
        pyqt_path = os.path.dirname(PyQt5.__file__)
        possible_paths.append(os.path.join(pyqt_path, 'Qt5', 'plugins'))
        possible_paths.append(os.path.join(pyqt_path, 'plugins'))
    except:
        pass
    
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = path
            print(f"Qt plugins path set to: {path}")
            break
    
    os.environ['QT_QPA_PLATFORM'] = 'windows'
    
    qt_bin_path = os.path.dirname(os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', ''))
    if qt_bin_path and os.path.exists(qt_bin_path):
        os.environ['PATH'] = qt_bin_path + os.pathsep + os.environ.get('PATH', '')

# Вызываем ДО импорта PyQt5
fix_qt_plugins()

# Теперь импортируем PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QLabel,
                             QMessageBox, QGroupBox, QTabWidget, QFrame)
from PyQt5.QtCore import Qt, QProcess, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client.config_manager import config_manager


class ClientProcess(QProcess):
    """Процесс клиента"""
    log_signal = pyqtSignal(str, str)
    
    def __init__(self, client_id, parent=None):
        super().__init__(parent)
        self.client_id = client_id
        self.readyReadStandardOutput.connect(self._read_stdout)
        self.readyReadStandardError.connect(self._read_stderr)
        self.finished.connect(self._on_finished)
    
    def start_client(self):
        self.start(sys.executable, ["client.py"])
        self.log_signal.emit(f"Клиент {self.client_id} запущен", "info")
    
    def _read_stdout(self):
        data = self.readAllStandardOutput().data().decode('utf-8', errors='replace')
        for line in data.splitlines():
            if line.strip():
                self.log_signal.emit(line.strip(), "info")
    
    def _read_stderr(self):
        data = self.readAllStandardError().data().decode('utf-8', errors='replace')
        for line in data.splitlines():
            if line.strip():
                self.log_signal.emit(line.strip(), "error")
    
    def _on_finished(self, exit_code, exit_status):
        self.log_signal.emit(f"Клиент {self.client_id} завершил работу (код: {exit_code})", "warning")
    
    def stop(self):
        if self.state() == QProcess.Running:
            self.terminate()
            QTimer.singleShot(3000, self.kill)


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clients = {}
        self.next_client_id = 1
        self.initUI()
        self.check_server_status()
        
        # Таймер проверки статуса
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_server_status)
        self.status_timer.start(5000)
    
    def initUI(self):
        self.setWindowTitle("ДПЖ - Лаунчер")
        self.setMinimumSize(900, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #2e2e2e; }
            QLabel { color: #e0e0e0; }
            QGroupBox { color: #e0e0e0; border: 1px solid #4a4a4a; border-radius: 8px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QPushButton { background-color: #4a4a4a; border: none; border-radius: 6px; padding: 8px 16px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #5a5a5a; }
            QPushButton:disabled { background-color: #3a3a3a; color: #666; }
            QTextEdit { background-color: #3a3a3a; border: 1px solid #4a4a4a; border-radius: 6px; color: #e0e0e0; font-family: monospace; }
            QTabWidget::pane { background-color: #3a3a3a; border-radius: 6px; }
            QTabBar::tab { background-color: #4a4a4a; color: #e0e0e0; padding: 8px 16px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #5a5a5a; }
            QTabBar::tab:hover { background-color: #6a6a6a; }
            QTabBar::close-button { background-color: #8b3a3a; border-radius: 2px; }
            QTabBar::close-button:hover { background-color: #a04040; }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("ДПЖ - Лаунчер")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e67e22; padding: 10px;")
        layout.addWidget(title)
        
        # Статус
        status_group = QGroupBox("Статус")
        status_layout = QHBoxLayout()
        
        self.server_status = QLabel("Проверка сервера...")
        status_layout.addWidget(self.server_status)
        status_layout.addStretch()
        self.clients_count = QLabel("Клиентов: 0")
        status_layout.addWidget(self.clients_count)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Кнопки
        controls_group = QGroupBox("Управление")
        controls_layout = QHBoxLayout()
        
        self.start_client_btn = QPushButton("Запустить клиента")
        self.start_client_btn.clicked.connect(self.start_client)
        self.start_client_btn.setEnabled(False)
        controls_layout.addWidget(self.start_client_btn)
        
        self.stop_clients_btn = QPushButton("Остановить всех")
        self.stop_clients_btn.clicked.connect(self.stop_all_clients)
        self.stop_clients_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_clients_btn)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Вкладки логов
        self.log_tabs = QTabWidget()
        
        # Логи сервера (информационные сообщения)
        self.server_log = QTextEdit()
        self.server_log.setReadOnly(True)
        self.server_log.setFont(QFont("Consolas", 10))
        self.log_tabs.addTab(self.server_log, "Логи")
        
        # Вкладки клиентов
        self.clients_tabs = QTabWidget()
        self.clients_tabs.setTabsClosable(True)
        self.clients_tabs.tabCloseRequested.connect(self.close_client_tab)
        self.log_tabs.addTab(self.clients_tabs, "Клиенты")
        
        layout.addWidget(self.log_tabs)
        
        central.setLayout(layout)
    
    def _separator(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.VLine)
        frame.setFixedWidth(2)
        frame.setStyleSheet("background-color: #4a4a4a;")
        return frame
    
    def _log(self, text_widget, message, log_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {"info": "#3498db", "error": "#e74c3c", "success": "#2ecc71", "warning": "#f39c12"}
        color = colors.get(log_type, "#e0e0e0")
        
        text_widget.append(f'<span style="color: #888;">[{timestamp}]</span> <span style="color: {color};">{message}</span>')
        
        cursor = text_widget.textCursor()
        cursor.movePosition(cursor.End)
        text_widget.setTextCursor(cursor)
    
    def check_server_status(self):
        success, msg = config_manager.test_connection()
        
        if success:
            self.server_status.setText(f"Сервер {config_manager.host}:{config_manager.port} - работает")
            self.server_status.setStyleSheet("color: #2ecc71;")
            self.start_client_btn.setEnabled(True)
            self._log(self.server_log, f"Сервер доступен", "success")
        else:
            self.server_status.setText(f"Сервер {config_manager.host}:{config_manager.port} - {msg}")
            self.server_status.setStyleSheet("color: #e74c3c;")
            self.start_client_btn.setEnabled(False)
        
        active = len(self.clients)
        self.clients_count.setText(f"Клиентов: {active}")
        self.stop_clients_btn.setEnabled(active > 0)
        return success
    
    def start_client(self):
        if not self.check_server_status():
            QMessageBox.warning(self, "Ошибка", "Сервер не доступен. Проверьте настройки подключения.")
            return
        
        client_id = self.next_client_id
        self.next_client_id += 1
        
        client = ClientProcess(client_id)
        client.log_signal.connect(lambda msg, t: self._client_log(client_id, msg, t))
        client.start_client()
        
        self.clients[client_id] = client
        
        # Создаём вкладку для клиента
        tab = QWidget()
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(text_edit)
        
        stop_btn = QPushButton(f"Остановить клиента {client_id}")
        stop_btn.clicked.connect(lambda: self.stop_client(client_id))
        layout.addWidget(stop_btn)
        
        tab.setLayout(layout)
        self.clients_tabs.addTab(tab, f"Клиент {client_id}")
        
        client.log_widget = text_edit
        self.check_server_status()
    
    def _client_log(self, client_id, message, log_type):
        for i in range(self.clients_tabs.count()):
            if self.clients_tabs.tabText(i) == f"Клиент {client_id}":
                widget = self.clients_tabs.widget(i)
                text_edit = widget.layout().itemAt(0).widget()
                self._log(text_edit, message, log_type)
                return
    
    def stop_client(self, client_id):
        if client_id in self.clients:
            self._client_log(client_id, "Остановка клиента...", "warning")
            self.clients[client_id].stop()
            self.cleanup_client(client_id)
    
    def stop_all_clients(self):
        for client_id in list(self.clients.keys()):
            self.stop_client(client_id)
    
    def cleanup_client(self, client_id):
        if client_id in self.clients:
            del self.clients[client_id]
            self.check_server_status()
            
            for i in range(self.clients_tabs.count()):
                if self.clients_tabs.tabText(i) == f"Клиент {client_id}":
                    self.clients_tabs.removeTab(i)
                    break
    
    def close_client_tab(self, index):
        tab_text = self.clients_tabs.tabText(index)
        try:
            client_id = int(tab_text.split()[1])
            self.stop_client(client_id)
        except:
            pass
    
    def closeEvent(self, event):
        self.stop_all_clients()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LauncherWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()