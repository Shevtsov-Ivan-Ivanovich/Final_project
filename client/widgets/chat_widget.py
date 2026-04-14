# client/widgets/chat_widget.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QLineEdit, QPushButton, QComboBox, QLabel,
                             QScrollBar)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat


class ChatWidget(QWidget):
    """Виджет чата с поддержкой различных типов сообщений"""
    
    message_sent = pyqtSignal(str, str)  # message, action_type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_history = []
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Область отображения чата
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                font-family: 'Segoe UI', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Панель ввода
        input_frame = QWidget()
        input_frame.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
                border-radius: 8px;
            }
        """)
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        # Выбор типа действия
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "💬 Обычный чат",
            "🎭 Действие",
            "📢 Объявление",
            "⚔️ Бой",
            "🎲 Бросок кубика",
            "🏃 Перемещение",
            "💊 Использование предмета"
        ])
        self.action_combo.setStyleSheet("""
            QComboBox {
                background-color: #4a4a4a;
                border: none;
                border-radius: 6px;
                padding: 6px;
                color: #e0e0e0;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #4a4a4a;
                color: #e0e0e0;
                selection-background-color: #5a5a5a;
            }
        """)
        input_layout.addWidget(self.action_combo)
        
        # Поле ввода сообщения
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setStyleSheet("""
            QLineEdit {
                background-color: #4a4a4a;
                border: none;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        # Кнопка отправки
        send_btn = QPushButton("📤 Отправить")
        send_btn.clicked.connect(self.send_message)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2d6a4f;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #40916c;
            }
        """)
        input_layout.addWidget(send_btn)
        
        input_frame.setLayout(input_layout)
        layout.addWidget(input_frame)
        
        self.setLayout(layout)
    
    def add_message(self, username: str, character_name: str, message: str, 
                    action_type: str = 'chat', timestamp: str = None):
        """Добавляет сообщение в чат"""
        from datetime import datetime
        
        if not timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        display_name = character_name if character_name else username
        
        # Определяем цвет и префикс в зависимости от типа действия
        colors = {
            'chat': ('#e0e0e0', ''),
            'action': ('#e67e22', '🎭 *'),
            'announcement': ('#e74c3c', '📢 '),
            'combat': ('#e74c3c', '⚔️ '),
            'dice': ('#3498db', '🎲 '),
            'move': ('#2ecc71', '🏃 '),
            'use_item': ('#9b59b6', '💊 ')
        }
        
        color, prefix = colors.get(action_type, ('#e0e0e0', ''))
        
        # Форматируем сообщение
        formatted = f'<span style="color: #888;">[{timestamp}]</span> '
        formatted += f'<span style="color: #f39c12;">{display_name}:</span> '
        formatted += f'<span style="color: {color};">{prefix}{self.escape_html(message)}</span>'
        
        self.chat_display.append(formatted)
        
        # Прокручиваем вниз
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Сохраняем в историю
        self.message_history.append({
            'timestamp': timestamp,
            'username': username,
            'character_name': character_name,
            'message': message,
            'action_type': action_type
        })
        
        # Ограничиваем историю
        if len(self.message_history) > 500:
            self.message_history = self.message_history[-500:]
    
    def add_system_message(self, message: str, message_type: str = 'info'):
        """Добавляет системное сообщение"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            'info': '#3498db',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'error': '#e74c3c'
        }
        
        color = colors.get(message_type, '#888')
        prefix = 'ℹ️ ' if message_type == 'info' else '⚠️ ' if message_type == 'warning' else '✅ ' if message_type == 'success' else '❌ '
        
        formatted = f'<span style="color: #888;">[{timestamp}]</span> '
        formatted += f'<span style="color: {color};">{prefix}{self.escape_html(message)}</span>'
        
        self.chat_display.append(formatted)
        
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def add_gm_message(self, message: str):
        """Добавляет сообщение от ГМ"""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted = f'<span style="color: #888;">[{timestamp}]</span> '
        formatted += f'<span style="color: #e74c3c; font-weight: bold;">[GM]</span> '
        formatted += f'<span style="color: #e0e0e0;">{self.escape_html(message)}</span>'
        
        self.chat_display.append(formatted)
        
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Отправляет сообщение"""
        message = self.message_input.text().strip()
        if not message:
            return
        
        action_type = self.action_combo.currentText()
        action_map = {
            "💬 Обычный чат": "chat",
            "🎭 Действие": "action",
            "📢 Объявление": "announcement",
            "⚔️ Бой": "combat",
            "🎲 Бросок кубика": "dice",
            "🏃 Перемещение": "move",
            "💊 Использование предмета": "use_item"
        }
        
        self.message_sent.emit(message, action_map.get(action_type, "chat"))
        self.message_input.clear()
    
    def roll_dice(self, dice_expression: str = "1d20"):
        """Бросает кубик и возвращает результат"""
        import random
        import re
        
        # Парсим выражение типа "2d6+3" или "1d20"
        match = re.match(r'(\d+)d(\d+)(?:[+-](\d+))?', dice_expression)
        
        if not match:
            return None, "Неверный формат. Используйте: XdY или XdY+Z"
        
        num = int(match.group(1))
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0
        
        rolls = [random.randint(1, sides) for _ in range(num)]
        total = sum(rolls) + modifier
        
        result_text = f"🎲 Бросок {dice_expression}: {rolls}"
        if modifier:
            result_text += f" + {modifier}"
        result_text += f" = {total}"
        
        return total, result_text
    
    def clear(self):
        """Очищает чат"""
        self.chat_display.clear()
        self.message_history.clear()
    
    def escape_html(self, text: str) -> str:
        """Экранирует HTML-символы"""
        return (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&#39;'))