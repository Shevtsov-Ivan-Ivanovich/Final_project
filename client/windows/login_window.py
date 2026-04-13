# client/windows/login_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QTimer
from client.api_client import api_client
from client.windows.role_window import RoleWindow


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setFixedSize(350, 450)
        self.setStyleSheet("""
            QDialog {
                background-color: #3a3a3a;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5a5a5a;
                border: none;
                border-radius: 6px;
                padding: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Регистрация")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        layout.addWidget(self.username_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Подтвердите пароль")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)
        
        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
    
    def handle_register(self):
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not all([username, email, password, confirm]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        
        user = api_client.register(username, email, password)
        if user:
            QMessageBox.information(self, "Успех", "Регистрация успешна!")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось зарегистрироваться")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("ДПЖ - Вход")
        self.setFixedSize(350, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #4a4a4a;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #5a5a5a;
                border: none;
                border-radius: 6px;
                padding: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("ДПЖ")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title)
        
        subtitle = QLabel("Система управления играми")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин или Email")
        layout.addWidget(self.login_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        
        self.login_btn = QPushButton("Вход")
        self.login_btn.clicked.connect(self.handle_login)
        layout.addWidget(self.login_btn)
        
        self.register_btn = QPushButton("Регистрация")
        self.register_btn.clicked.connect(self.handle_register)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
    
    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        user = api_client.login(login, password)
        if user:
            self.user_data = user
            QMessageBox.information(self, "Успех", f"Добро пожаловать, {user['username']}!")
            self.after_login()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
    
    def handle_register(self):
        dialog = RegisterDialog(self)
        if dialog.exec_():
            self.login_input.clear()
            self.password_input.clear()
    
    def after_login(self):
        self.role_window = RoleWindow(self.user_data)
        self.role_window.show()
        self.close()