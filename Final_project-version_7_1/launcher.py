# launcher.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

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
    
    for path in possible_paths:
        if os.path.exists(path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = path
            print(f"Qt plugins path set to: {path}")
            break
    
    os.environ['QT_QPA_PLATFORM'] = 'windows'
    
    qt_bin_path = os.path.dirname(os.environ.get('QT_QPA_PLATFORM_PLUGIN_PATH', ''))
    if qt_bin_path and os.path.exists(qt_bin_path):
        os.environ['PATH'] = qt_bin_path + os.pathsep + os.environ.get('PATH', '')

fix_qt_plugins()

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QMessageBox, QTabWidget, QFrame, QGroupBox,
                             QLineEdit, QDialog, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCursor

import json
import requests
from datetime import datetime

from client.network_config import network_config


class ClientThread(QThread):
    log_signal = pyqtSignal(str, str)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.is_running = False
    
    def run(self):
        try:
            self.process = subprocess.Popen(
                [sys.executable, 'client.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            self.is_running = True
            
            def read_output(pipe, log_type):
                try:
                    for line in iter(pipe.readline, b''):
                        if line:
                            try:
                                decoded_line = line.decode('utf-8', errors='ignore')
                            except:
                                decoded_line = str(line)
                            if decoded_line.strip():
                                self.log_signal.emit(decoded_line.strip(), log_type)
                except Exception as e:
                    self.log_signal.emit(f"Error reading {log_type}: {e}", 'error')
            
            stdout_thread = threading.Thread(target=read_output, args=(self.process.stdout, 'client'))
            stderr_thread = threading.Thread(target=read_output, args=(self.process.stderr, 'error'))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()
            
            self.process.wait()
            
        except Exception as e:
            self.log_signal.emit(f"Ошибка запуска клиента: {e}", 'error')
        finally:
            self.is_running = False
    
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            QTimer.singleShot(2000, self.kill_process)
    
    def kill_process(self):
        if self.process and self.process.poll() is None:
            self.process.kill()
        self.is_running = False


class SettingsDialog(QDialog):
    """Диалог настроек подключения к серверу"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки подключения")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Настройки подключения к серверу")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.host_input = QLineEdit()
        self.host_input.setText(network_config.host)
        self.host_input.setPlaceholderText("IP адрес сервера")
        form_layout.addRow("IP адрес:", self.host_input)
        
        self.port_input = QLineEdit()
        self.port_input.setText(str(network_config.port))
        self.port_input.setPlaceholderText("Порт")
        form_layout.addRow("Порт:", self.port_input)
        
        layout.addLayout(form_layout)
        
        # Статус подключения
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Кнопка проверки
        test_btn = QPushButton("Проверить подключение")
        test_btn.clicked.connect(self.test_connection)
        layout.addWidget(test_btn)
        
        # Кнопки
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.save_and_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self.setLayout(layout)
    
    def test_connection(self):
        """Проверяет подключение к серверу"""
        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip()) if self.port_input.text().strip() else 5000
        
        try:
            response = requests.get(f"http://{host}:{port}/api/health", timeout=3)
            if response.status_code == 200:
                self.status_label.setText("✅ Подключение успешно!")
                self.status_label.setStyleSheet("color: #2ecc71;")
            else:
                self.status_label.setText(f"❌ Ошибка: код {response.status_code}")
                self.status_label.setStyleSheet("color: #e74c3c;")
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка подключения: {str(e)[:50]}")
            self.status_label.setStyleSheet("color: #e74c3c;")
    
    def save_and_accept(self):
        """Сохраняет настройки и закрывает диалог"""
        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip()) if self.port_input.text().strip() else 5000
        
        network_config.save_config(host, port)
        self.accept()


class LauncherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client_thread = None
        self.client_started = False
        
        self.initUI()
        self.check_server_status()
        
        # Таймер для проверки статуса сервера
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_server_status)
        self.status_timer.start(5000)
    
    def initUI(self):
        self.setWindowTitle("ДПЖ - Лаунчер")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(self.get_stylesheet())
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Заголовок
        title_label = QLabel("🎮 ДПЖ - Система управления играми 🎲")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e67e22; padding: 15px;")
        main_layout.addWidget(title_label)
        
        # Информационная панель
        info_frame = QFrame()
        info_frame.setStyleSheet("QFrame { background-color: #3a3a3a; border-radius: 10px; padding: 15px; }")
        info_layout = QHBoxLayout()
        
        self.status_label = QLabel("⚙️ Статус: Ожидание")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.status_label)
        
        info_layout.addStretch()
        
        self.server_status = QLabel("🔴 Сервер: Проверка...")
        self.server_status.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.server_status)
        
        self.client_status = QLabel("🔴 Клиент: Остановлен")
        self.client_status.setStyleSheet("font-size: 14px;")
        info_layout.addWidget(self.client_status)
        
        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)
        
        # Вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { background-color: #2e2e2e; border-radius: 8px; }
            QTabBar::tab { background-color: #3a3a3a; color: #e0e0e0; padding: 8px 20px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #e67e22; }
        """)
        
        control_tab = self.create_control_tab()
        tabs.addTab(control_tab, "🎮 Управление")
        
        logs_tab = self.create_logs_tab()
        tabs.addTab(logs_tab, "📋 Логи")
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
    
    def get_stylesheet(self):
        return """
            QMainWindow { background-color: #2e2e2e; }
            QLabel { color: #e0e0e0; }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#start_client {
                background-color: #2d6a4f;
            }
            QPushButton#start_client:hover {
                background-color: #40916c;
            }
            QPushButton#stop_client {
                background-color: #8b3a3a;
            }
            QPushButton#stop_client:hover {
                background-color: #a04040;
            }
            QPushButton#settings_btn {
                background-color: #3498db;
            }
            QPushButton#settings_btn:hover {
                background-color: #2980b9;
            }
            QTextEdit {
                background-color: #3a3a3a;
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 5px;
                font-family: monospace;
            }
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
    
    def create_control_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Информация о сервере
        server_info_group = QGroupBox("Информация о сервере")
        server_info_layout = QVBoxLayout()
        
        self.server_info_label = QLabel(f"🌐 Адрес сервера: {network_config.host}:{network_config.port}")
        server_info_layout.addWidget(self.server_info_label)
        
        settings_btn = QPushButton("⚙️ Настройки подключения")
        settings_btn.setObjectName("settings_btn")
        settings_btn.clicked.connect(self.open_settings)
        server_info_layout.addWidget(settings_btn)
        
        server_info_group.setLayout(server_info_layout)
        layout.addWidget(server_info_group)
        
        # Группа клиента
        client_group = QGroupBox("Управление клиентом")
        client_layout = QVBoxLayout()
        
        client_btn_layout = QHBoxLayout()
        
        self.start_client_btn = QPushButton("🎮 ЗАПУСТИТЬ КЛИЕНТ")
        self.start_client_btn.setObjectName("start_client")
        self.start_client_btn.setMinimumHeight(50)
        self.start_client_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.start_client_btn.clicked.connect(self.start_client)
        client_btn_layout.addWidget(self.start_client_btn)
        
        self.stop_client_btn = QPushButton("🛑 ОСТАНОВИТЬ КЛИЕНТ")
        self.stop_client_btn.setObjectName("stop_client")
        self.stop_client_btn.setMinimumHeight(50)
        self.stop_client_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.stop_client_btn.clicked.connect(self.stop_client)
        self.stop_client_btn.setEnabled(False)
        client_btn_layout.addWidget(self.stop_client_btn)
        
        client_layout.addLayout(client_btn_layout)
        client_group.setLayout(client_layout)
        layout.addWidget(client_group)
        
        # Информация
        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        info_text.setPlainText(f"""
ДПЖ - Система управления играми (HTTP Polling версия)

Порядок запуска:
1. Запустите сервер через server/run.py
2. Убедитесь что сервер работает (статус должен стать зеленым)
3. Нажмите "Запустить клиент"
4. Войдите в аккаунт (admin / admin123)
5. Выберите роль и начните игру!

Текущий адрес сервера: {network_config.host}:{network_config.port}
Для изменения адреса используйте кнопку "Настройки подключения"
        """.strip())
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.logs_text)
        
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Очистить")
        clear_btn.clicked.connect(self.clear_logs)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        layout.addLayout(btn_layout)
        
        tab.setLayout(layout)
        return tab
    
    def open_settings(self):
        """Открывает окно настроек"""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Обновляем отображение
            self.server_info_label.setText(f"🌐 Адрес сервера: {network_config.host}:{network_config.port}")
            self.check_server_status()
            self.add_log(f"Настройки обновлены: {network_config.host}:{network_config.port}", 'info')
    
    def check_server_status(self):
        """Проверяет статус сервера"""
        try:
            response = requests.get(f"http://{network_config.host}:{network_config.port}/api/health", timeout=3)
            if response.status_code == 200:
                self.server_status.setText("🟢 Сервер: Работает")
                self.server_status.setStyleSheet("color: #2ecc71; font-size: 14px;")
                return True
            else:
                self.server_status.setText("🔴 Сервер: Не отвечает")
                self.server_status.setStyleSheet("color: #e74c3c; font-size: 14px;")
                return False
        except Exception as e:
            self.server_status.setText(f"🔴 Сервер: Недоступен")
            self.server_status.setStyleSheet("color: #e74c3c; font-size: 14px;")
            return False
    
    def start_client(self):
        if self.client_started:
            self.add_log("Клиент уже запущен", 'warning')
            return
        
        # Проверяем доступность сервера
        if not self.check_server_status():
            reply = QMessageBox.question(
                self, 
                "Сервер недоступен", 
                f"Сервер {network_config.host}:{network_config.port} не отвечает.\n"
                "Убедитесь что сервер запущен.\n\n"
                "Продолжить запуск клиента?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.add_log("Запуск клиента...", 'info')
        self.status_label.setText("⚙️ Статус: Запуск клиента...")
        
        self.client_thread = ClientThread()
        self.client_thread.log_signal.connect(self.add_log)
        self.client_thread.start()
        
        QTimer.singleShot(2000, self.check_client_started)
    
    def check_client_started(self):
        if self.client_thread and self.client_thread.is_running:
            self.client_started = True
            self.client_status.setText("🟢 Клиент: Запущен")
            self.start_client_btn.setEnabled(False)
            self.stop_client_btn.setEnabled(True)
            self.status_label.setText("✅ Статус: Клиент запущен")
            self.add_log("✅ Клиент запущен", 'success')
    
    def stop_client(self):
        if not self.client_started:
            return
        
        self.add_log("Остановка клиента...", 'info')
        if self.client_thread:
            self.client_thread.stop()
            self.client_thread = None
        
        self.client_started = False
        self.client_status.setText("🔴 Клиент: Остановлен")
        self.start_client_btn.setEnabled(True)
        self.stop_client_btn.setEnabled(False)
        self.status_label.setText("⚙️ Статус: Клиент остановлен")
        self.add_log("Клиент остановлен", 'info')
    
    def add_log(self, message, log_type='info'):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {'info': '#3498db', 'error': '#e74c3c', 'warning': '#f39c12', 
                  'success': '#2ecc71', 'client': '#e67e22'}
        prefixes = {'info': '[INFO]', 'error': '[ERROR]', 'warning': '[WARN]', 
                    'success': '[OK]', 'client': '[CLIENT]'}
        
        color = colors.get(log_type, '#e0e0e0')
        prefix = prefixes.get(log_type, '[LOG]')
        
        formatted_message = f'<span style="color: #888;">[{timestamp}]</span> <span style="color: {color};">{prefix}</span> <span style="color: #e0e0e0;">{message}</span>'
        
        self.logs_text.append(formatted_message)
        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logs_text.setTextCursor(cursor)
    
    def clear_logs(self):
        self.logs_text.clear()
        self.add_log("Логи очищены", 'info')
    
    def closeEvent(self, event):
        self.stop_client()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = LauncherWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    # Импортируем threading здесь, чтобы избежать циклических импортов
    import threading
    main()