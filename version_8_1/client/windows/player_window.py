# client/windows/player_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSplitter, QListWidget,
                             QTextEdit, QLineEdit, QComboBox, QMessageBox,
                             QGroupBox, QGridLayout, QProgressBar, QDialog)
from PyQt5.QtCore import Qt, QTimer
from client.api_client import api_client
from client.socket_client import SocketClient  # Импортируем КЛАСС
from client.config_manager import config_manager


class PlayerWindow(QWidget):
    def __init__(self, user_data, session_data, character_data):
        super().__init__()
        self.user_data = user_data
        self.session_data = session_data
        self.character_data = character_data
        self.inventory = []
        
        # СОЗДАЁМ ЭКЗЕМПЛЯР SocketClient
        self.socket_client = SocketClient()
        
        print(f"[PLAYER] ========== PLAYER WINDOW INIT ==========")
        print(f"[PLAYER] User: {user_data.get('username')} (ID: {user_data.get('id')})")
        print(f"[PLAYER] Session: {session_data.get('name')} (ID: {session_data.get('id')})")
        print(f"[PLAYER] Character: {character_data.get('name')} (ID: {character_data.get('id')})")
        
        self.initUI()
        self.setup_socket()
        self.connect_to_session()
        self.load_inventory()
        
        print(f"[PLAYER] PlayerWindow initialized successfully")
    
    def initUI(self):
        self.setWindowTitle(f"ДПЖ - Игрок | {self.character_data['name']} | Сессия: {self.session_data['name']}")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Верхняя панель
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # Основной сплиттер (лево - статы, право - инвентарь)
        top_splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - характеристики
        left_panel = self.create_stats_panel()
        top_splitter.addWidget(left_panel)
        
        # Правая панель - инвентарь
        right_panel = self.create_inventory_panel()
        top_splitter.addWidget(right_panel)
        
        top_splitter.setSizes([400, 800])
        main_layout.addWidget(top_splitter)
        
        # Нижняя панель - чат
        bottom_panel = self.create_chat_panel()
        main_layout.addWidget(bottom_panel)
        
        self.setLayout(main_layout)
        
        # Таймер для обновления данных
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(5000)
    
    def get_stylesheet(self):
        return """
            QWidget {
                background-color: #2e2e2e;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QFrame {
                background-color: #3a3a3a;
                border-radius: 8px;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
            QListWidget::item:selected {
                background-color: #5a5a5a;
            }
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #e0e0e0;
                font-family: monospace;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
            }
            QComboBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 6px;
                color: #e0e0e0;
            }
            QProgressBar {
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
            QGroupBox {
                color: #e0e0e0;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
    
    def create_top_panel(self):
        panel = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        info_label = QLabel(f"🎭 {self.character_data['name']} | Сессия: {self.session_data['name']}")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e67e22;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.connection_status = QLabel("🔴 Подключение...")
        layout.addWidget(self.connection_status)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        exit_btn = QPushButton("🚪 Выйти")
        exit_btn.setObjectName("danger")
        exit_btn.clicked.connect(self.exit_session)
        layout.addWidget(exit_btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_stats_panel(self):
        panel = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        title = QLabel("Характеристики персонажа")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title)
        
        # HP
        hp_group = QGroupBox("❤️ Здоровье")
        hp_layout = QVBoxLayout()
        
        self.hp_label = QLabel(f"{self.character_data.get('current_hp', 10)} / {self.character_data.get('max_hp', 10)}")
        self.hp_label.setAlignment(Qt.AlignCenter)
        self.hp_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #e74c3c;")
        hp_layout.addWidget(self.hp_label)
        
        self.hp_bar = QProgressBar()
        hp_percent = (self.character_data.get('current_hp', 10) / self.character_data.get('max_hp', 10)) * 100
        self.hp_bar.setValue(int(hp_percent))
        hp_layout.addWidget(self.hp_bar)
        
        hp_group.setLayout(hp_layout)
        layout.addWidget(hp_group)
        
        # MP
        mp_group = QGroupBox("💙 Мана")
        mp_layout = QVBoxLayout()
        
        self.mp_label = QLabel(f"{self.character_data.get('current_mp', 5)} / {self.character_data.get('max_mp', 5)}")
        self.mp_label.setAlignment(Qt.AlignCenter)
        self.mp_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #3498db;")
        mp_layout.addWidget(self.mp_label)
        
        self.mp_bar = QProgressBar()
        mp_percent = (self.character_data.get('current_mp', 5) / self.character_data.get('max_mp', 5)) * 100
        self.mp_bar.setValue(int(mp_percent))
        mp_layout.addWidget(self.mp_bar)
        
        mp_group.setLayout(mp_layout)
        layout.addWidget(mp_group)
        
        # Базовые характеристики
        stats_group = QGroupBox("📊 Атрибуты")
        stats_layout = QGridLayout()
        
        stats = [
            ('💪 Сила', 'strength', self.character_data.get('strength', 10)),
            ('🏃 Ловкость', 'dexterity', self.character_data.get('dexterity', 10)),
            ('🧠 Интеллект', 'intelligence', self.character_data.get('intelligence', 10)),
            ('💬 Харизма', 'charisma', self.character_data.get('charisma', 10)),
            ('⭐ Уровень', 'level', self.character_data.get('level', 1)),
            ('📈 Опыт', 'experience', self.character_data.get('experience', 0))
        ]
        
        for i, (name, key, value) in enumerate(stats):
            row = i // 2
            col = i % 2 * 2
            stats_layout.addWidget(QLabel(name), row, col)
            
            label = QLabel(str(value))
            label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f39c12;")
            label.setAlignment(Qt.AlignCenter)
            stats_layout.addWidget(label, row, col + 1)
            setattr(self, f"{key}_label", label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_inventory_panel(self):
        panel = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title = QLabel("📦 Инвентарь")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2ecc71;")
        layout.addWidget(title)
        
        self.inventory_list = QListWidget()
        self.inventory_list.itemDoubleClicked.connect(self.use_item)
        layout.addWidget(self.inventory_list)
        
        equip_title = QLabel("⚔️ Экипировано")
        equip_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #f39c12; margin-top: 10px;")
        layout.addWidget(equip_title)
        
        self.equipped_list = QListWidget()
        self.equipped_list.setMaximumHeight(150)
        self.equipped_list.itemDoubleClicked.connect(self.unequip_item)
        layout.addWidget(self.equipped_list)
        
        panel.setLayout(layout)
        return panel
    
    def create_chat_panel(self):
        panel = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 10)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        self.chat_display.setStyleSheet("background-color: #2a2a2a;")
        layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        
        self.action_combo = QComboBox()
        self.action_combo.addItems([
            "💬 Обычный чат",
            "🎭 Действие",
            "⚔️ Бой",
            "🎲 Бросок кубика"
        ])
        input_layout.addWidget(self.action_combo)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("Отправить")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        panel.setLayout(layout)
        return panel
    
    def setup_socket(self):
        # Подключаем сигналы к ЭКЗЕМПЛЯРУ socket_client (НЕ к классу!)
        self.socket_client.connected_signal.connect(self.on_socket_connected)
        self.socket_client.disconnected_signal.connect(self.on_socket_disconnected)
        self.socket_client.chat_signal.connect(self.on_chat_message)
        self.socket_client.character_updated_signal.connect(self.on_character_updated)
        self.socket_client.item_added_signal.connect(self.on_item_added)
        self.socket_client.item_removed_signal.connect(self.on_item_removed)
    
    def connect_to_session(self):
        from client.config_manager import config_manager
        
        server_ip = config_manager.host
        server_port = config_manager.port
        
        print(f"\n{'='*60}")
        print(f"[PLAYER] CONNECTING TO SESSION")
        print(f"[PLAYER] Server: {server_ip}:{server_port}")
        print(f"[PLAYER] Session ID: {self.session_data['id']}")
        print(f"[PLAYER] Character ID: {self.character_data['id']}")
        print(f"[PLAYER] Character Name: {self.character_data['name']}")
        print(f"[PLAYER] User ID: {self.user_data['id']}")
        print(f"{'='*60}\n")
        
        # Устанавливаем URL
        self.socket_client.base_url = f"http://{server_ip}:{server_port}"
        
        # Подключаемся через connect_player
        result = self.socket_client.connect_player(
            self.session_data['id'],
            self.user_data['id'],
            self.user_data['username'],
            self.character_data['id'],
            self.character_data['name']
        )
        
        if result:
            print(f"[PLAYER] ✅ Connected successfully!")
            self.connection_status.setText("🟢 Подключено")
            self.socket_client.get_players()
        else:
            print(f"[PLAYER] ❌ Connection failed!")
            self.connection_status.setText("🔴 Ошибка подключения")
            QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к сессии")

    def load_inventory(self):
        items = api_client.get_character_inventory(self.character_data['id'])
        self.inventory = items
        self.update_inventory_display()
    
    def update_inventory_display(self):
        self.inventory_list.clear()
        self.equipped_list.clear()
        
        for item in self.inventory:
            item_data = item.get('item_data', {})
            name = item.get('custom_name') or item_data.get('name', '?')
            icon = item_data.get('icon', '📦')
            qty = f" x{item['quantity']}" if item['quantity'] > 1 else ""
            description = item_data.get('description', '')
            
            display_text = f"{icon} {name}{qty}"
            if description:
                display_text += f"\n  {description}"
            
            if item.get('is_equipped'):
                self.equipped_list.addItem(display_text)
                self.equipped_list.item(self.equipped_list.count() - 1).setData(Qt.UserRole, item['item_id'])
            else:
                self.inventory_list.addItem(display_text)
                self.inventory_list.item(self.inventory_list.count() - 1).setData(Qt.UserRole, item['item_id'])
    
    def use_item(self, item):
        current = self.inventory_list.currentItem()
        if not current:
            return
        
        item_id = current.data(Qt.UserRole)
        item = next((i for i in self.inventory if i['item_id'] == item_id), None)
        
        if item:
            item_data = item.get('item_data', {})
            
            if item_data.get('is_equippable'):
                if api_client.equip_item(self.character_data['id'], item_id):
                    self.load_inventory()
                    self.socket_client.send_chat(f"экипировал {item_data.get('name', 'предмет')}", "action")
            elif item_data.get('item_type') == 'consumable':
                effects = item_data.get('effects', {})
                
                if 'heal_hp' in effects:
                    new_hp = min(self.character_data.get('current_hp', 10) + effects['heal_hp'],
                                self.character_data.get('max_hp', 10))
                    self.update_character_stat('current_hp', new_hp)
                    self.socket_client.send_chat(f"использовал {item_data.get('name')} и восстановил {effects['heal_hp']} HP", "action")
                
                if 'heal_mp' in effects:
                    new_mp = min(self.character_data.get('current_mp', 5) + effects['heal_mp'],
                                self.character_data.get('max_mp', 5))
                    self.update_character_stat('current_mp', new_mp)
                    self.socket_client.send_chat(f"использовал {item_data.get('name')} и восстановил {effects['heal_mp']} MP", "action")
                
                api_client.remove_item_from_character(self.character_data['id'], item_id)
                self.load_inventory()
    
    def unequip_item(self, item):
        current = self.equipped_list.currentItem()
        if not current:
            return
        
        item_id = current.data(Qt.UserRole)
        if api_client.unequip_item(self.character_data['id'], item_id):
            self.load_inventory()
            self.socket_client.send_chat("снял предмет", "action")
    
    def update_character_stat(self, stat_name, value):
        updates = {stat_name: value}
        api_client.update_character(self.character_data['id'], updates)
        self.character_data[stat_name] = value
        self.update_stats_display()
    
    def update_stats_display(self):
        self.hp_label.setText(f"{self.character_data.get('current_hp', 10)} / {self.character_data.get('max_hp', 10)}")
        hp_percent = (self.character_data.get('current_hp', 10) / self.character_data.get('max_hp', 10)) * 100
        self.hp_bar.setValue(int(hp_percent))
        
        self.mp_label.setText(f"{self.character_data.get('current_mp', 5)} / {self.character_data.get('max_mp', 5)}")
        mp_percent = (self.character_data.get('current_mp', 5) / self.character_data.get('max_mp', 5)) * 100
        self.mp_bar.setValue(int(mp_percent))

        self.strength_label.setText(str(self.character_data.get('strength', 10)))
        self.dexterity_label.setText(str(self.character_data.get('dexterity', 10)))
        self.intelligence_label.setText(str(self.character_data.get('intelligence', 10)))
        self.charisma_label.setText(str(self.character_data.get('charisma', 10)))
        self.level_label.setText(str(self.character_data.get('level', 1)))
        self.experience_label.setText(str(self.character_data.get('experience', 0)))

        self.repaint()
        
    def refresh_data(self):
        characters = api_client.get_my_characters(self.user_data['id'])
        for char in characters:
            if char['id'] == self.character_data['id']:
                self.character_data = char
                break
        
        self.update_stats_display()
        self.load_inventory()
    
    # Socket обработчики
    def on_socket_connected(self):
        self.connection_status.setText("🟢 Подключено")
        self.connection_status.setStyleSheet("color: #2ecc71;")
    
    def on_socket_disconnected(self):
        self.connection_status.setText("🔴 Отключено")
        self.connection_status.setStyleSheet("color: #e74c3c;")
    
    def on_chat_message(self, data):
        timestamp = data.get('timestamp', '??:??')
        character = data.get('character_name', data.get('username', '?'))
        message = data.get('message', '')
        action_type = data.get('action_type', 'chat')
        
        prefix = ""
        if action_type == 'action':
            prefix = "🎭 *"
        elif action_type == 'combat':
            prefix = "⚔️ "
        elif action_type == 'dice':
            prefix = "🎲 "
        
        self.chat_display.append(f"[{timestamp}] {character}: {prefix}{message}")
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_character_updated(self, data):
        print(f"[PLAYER] on_character_updated received: {data}")
        if data['character_id'] == self.character_data['id']:
            for key, value in data['updates'].items():
                self.character_data[key] = value
            self.update_stats_display()
    
    def on_item_added(self, data):
        if data['character_id'] == self.character_data['id']:
            self.load_inventory()
            self.chat_display.append(f"📦 ГМ выдал вам предмет")
    
    def on_item_removed(self, data):
        if data['character_id'] == self.character_data['id']:
            self.load_inventory()
            self.chat_display.append(f"🗑 ГМ удалил у вас предмет")
    
    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return
        
        action_type = self.action_combo.currentText()
        action_map = {
            "💬 Обычный чат": "chat",
            "🎭 Действие": "action",
            "⚔️ Бой": "combat",
            "🎲 Бросок кубика": "dice"
        }
        
        self.socket_client.send_chat(message, action_map.get(action_type, "chat"))
        self.message_input.clear()
    
    def exit_session(self):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти из игры?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Выходим из сессии
            api_client.leave_session(self.session_data['id'], self.user_data['id'])
            if hasattr(self, 'socket_client'):
                self.socket_client.disconnect()
            self.close()