# client/windows/gm_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSplitter, QListWidget,
                             QTextEdit, QLineEdit, QComboBox, QMessageBox,
                             QTabWidget, QGroupBox, QDialog, QInputDialog,
                             QListWidgetItem, QMenu, QAction, QScrollArea,
                             QGridLayout, QSpinBox)
from PyQt5.QtCore import Qt, QTimer
from client.api_client import api_client
from client.socket_client import SocketClient  # Импортируем класс
from client.windows.story_dialog import StoryDialog


class GMWindow(QWidget):
    def __init__(self, user_data, session_data):
        super().__init__()
        self.user_data = user_data
        self.session_data = session_data
        self.players = {}  # user_id -> player_data
        self.game_objects = {'locations': [], 'npcs': [], 'monsters': []}
        
        # СОЗДАЁМ НОВЫЙ ЭКЗЕМПЛЯР SocketClient
        self.socket_client = SocketClient()
        
        self.initUI()
        self.setup_socket()
        self.connect_to_session()
        self.load_game_objects()
    
    def initUI(self):
        self.setWindowTitle(f"ДПЖ - Гейм Мастер | Сессия: {self.session_data['name']}")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(self.get_stylesheet())
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Верхняя панель
        top_panel = self.create_top_panel()
        main_layout.addWidget(top_panel)
        
        # Основной сплиттер
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Левая панель - управление
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Правая панель - игроки и объекты
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([400, 800])
        main_layout.addWidget(main_splitter)
        
        # Нижняя панель - чат
        bottom_panel = self.create_bottom_panel()
        main_layout.addWidget(bottom_panel)
        
        self.setLayout(main_layout)
    
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
            QPushButton#danger {
                background-color: #8b3a3a;
            }
            QPushButton#danger:hover {
                background-color: #a04040;
            }
            QPushButton#success {
                background-color: #2d6a4f;
            }
            QPushButton#success:hover {
                background-color: #40916c;
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
            QTabWidget::pane {
                background-color: #3a3a3a;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5a5a5a;
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
            QScrollArea {
                border: none;
            }
        """
    
    def create_top_panel(self):
        panel = QFrame()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        info_label = QLabel(f"🎮 Сессия: {self.session_data['name']}")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e67e22;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        self.connection_status = QLabel("🟢 Подключено")
        self.connection_status.setStyleSheet("color: #2ecc71;")
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
    
    def create_left_panel(self):
        panel = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        btn_group = QGroupBox("Управление")
        btn_layout = QVBoxLayout()
        
        self.players_btn = QPushButton("👥 Персонажи игроков")
        self.players_btn.clicked.connect(self.show_players_management)
        btn_layout.addWidget(self.players_btn)
        
        self.story_btn = QPushButton("📖 Создать сюжет")
        self.story_btn.clicked.connect(self.open_story_dialog)
        btn_layout.addWidget(self.story_btn)
        
        self.items_btn = QPushButton("📦 Управление предметами")
        self.items_btn.clicked.connect(self.show_items_management)
        btn_layout.addWidget(self.items_btn)
        
        btn_group.setLayout(btn_layout)
        layout.addWidget(btn_group)
        
        log_group = QGroupBox("Логи действий")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        
        clear_logs_btn = QPushButton("Очистить логи")
        clear_logs_btn.clicked.connect(lambda: self.log_text.clear())
        log_layout.addWidget(clear_logs_btn)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        panel = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        splitter = QSplitter(Qt.Vertical)
        
        players_group = QGroupBox("Игроки в сессии")
        players_layout = QVBoxLayout()
        
        self.players_list = QListWidget()
        self.players_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.players_list.customContextMenuRequested.connect(self.show_player_context_menu)
        players_layout.addWidget(self.players_list)
        
        players_group.setLayout(players_layout)
        splitter.addWidget(players_group)
        
        objects_group = QGroupBox("Игровые объекты")
        objects_layout = QVBoxLayout()
        
        objects_tabs = QTabWidget()
        
        locations_tab = QWidget()
        locations_layout = QVBoxLayout()
        self.locations_list = QListWidget()
        self.locations_list.itemDoubleClicked.connect(lambda item: self.edit_game_object('location', item))
        locations_layout.addWidget(self.locations_list)
        add_location_btn = QPushButton("➕ Добавить локацию")
        add_location_btn.clicked.connect(lambda: self.add_game_object('location'))
        locations_layout.addWidget(add_location_btn)
        locations_tab.setLayout(locations_layout)
        objects_tabs.addTab(locations_tab, "📍 Локации")
        
        npcs_tab = QWidget()
        npcs_layout = QVBoxLayout()
        self.npcs_list = QListWidget()
        self.npcs_list.itemDoubleClicked.connect(lambda item: self.edit_game_object('npc', item))
        npcs_layout.addWidget(self.npcs_list)
        add_npc_btn = QPushButton("➕ Добавить NPC")
        add_npc_btn.clicked.connect(lambda: self.add_game_object('npc'))
        npcs_layout.addWidget(add_npc_btn)
        npcs_tab.setLayout(npcs_layout)
        objects_tabs.addTab(npcs_tab, "👤 NPC")
        
        monsters_tab = QWidget()
        monsters_layout = QVBoxLayout()
        self.monsters_list = QListWidget()
        self.monsters_list.itemDoubleClicked.connect(lambda item: self.edit_game_object('monster', item))
        monsters_layout.addWidget(self.monsters_list)
        add_monster_btn = QPushButton("➕ Добавить монстра")
        add_monster_btn.clicked.connect(lambda: self.add_game_object('monster'))
        monsters_layout.addWidget(add_monster_btn)
        monsters_tab.setLayout(monsters_layout)
        objects_tabs.addTab(monsters_tab, "👹 Монстры")
        
        objects_layout.addWidget(objects_tabs)
        objects_group.setLayout(objects_layout)
        splitter.addWidget(objects_group)
        
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)
        
        panel.setLayout(layout)
        return panel
    
    def create_bottom_panel(self):
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
            "📢 Объявление",
            "⚔️ Бой",
            "🎲 Бросок кубика",
            "🏃 Перемещение",
            "💊 Использование предмета"
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
        # Подключаем сигналы к ЭКЗЕМПЛЯРУ socket_client
        self.socket_client.connected_signal.connect(self.on_socket_connected)
        self.socket_client.disconnected_signal.connect(self.on_socket_disconnected)
        self.socket_client.chat_signal.connect(self.on_chat_message)
        self.socket_client.players_list_signal.connect(self.on_players_list)
        self.socket_client.character_updated_signal.connect(self.on_character_updated)
        self.socket_client.item_added_signal.connect(self.on_item_added)
        self.socket_client.item_removed_signal.connect(self.on_item_removed)
        self.socket_client.game_object_added_signal.connect(self.on_game_object_added)
        self.socket_client.player_joined_signal.connect(self.on_player_joined)
        self.socket_client.player_disconnected_signal.connect(self.on_player_disconnected)

    def connect_to_session(self):
        """Подключается к сессии как ГМ"""
        from client.config_manager import config_manager
        
        # Обновляем URL
        self.socket_client.base_url = f"http://{config_manager.host}:{config_manager.port}"
        
        # Регистрируемся как ГМ (используем connect_gm, НЕ register_gm)
        result = self.socket_client.connect_gm(
            self.session_data['id'],
            self.user_data['id'],
            self.user_data['username']
        )
        
        if result:
            print(f"[GM] Registered as GM for session {self.session_data['id']}")
            self.connection_status.setText("🟢 Подключено")
            self.connection_status.setStyleSheet("color: #2ecc71;")
            
            # Загружаем игроков
            QTimer.singleShot(500, lambda: self.socket_client.get_players())
        else:
            print(f"[GM] Failed to register as GM")
            self.connection_status.setText("🔴 Ошибка подключения")
            self.connection_status.setStyleSheet("color: #e74c3c;")
        
        # Загружаем логи
        self.load_logs()

    def load_logs(self):
        logs = api_client.get_session_logs(self.session_data['id'])
        for log in logs[:50]:
            timestamp = log['timestamp'][11:16] if log['timestamp'] else '??:??'
            performer = log.get('performer_name', '?')
            message = log.get('message', log.get('action_type', ''))
            self.log_text.append(f"[{timestamp}] {performer}: {message}")
    
    def load_game_objects(self):
        contexts = api_client.get_session_contexts(self.session_data['id'])
        for ctx in contexts:
            ctx_type = ctx['context_type']
            if ctx_type == 'location':
                self.game_objects['locations'].append(ctx)
                self.locations_list.addItem(f"📍 {ctx['name']}")
            elif ctx_type == 'npc':
                self.game_objects['npcs'].append(ctx)
                self.npcs_list.addItem(f"👤 {ctx['name']}")
            elif ctx_type == 'monster':
                self.game_objects['monsters'].append(ctx)
                self.monsters_list.addItem(f"👹 {ctx['name']}")
    
    def refresh_data(self):
        self.socket_client.get_players()
        self.load_logs()
    
    def show_players_management(self):
        """Показывает окно управления персонажами игроков"""
        if not self.players:
            QMessageBox.information(self, "Информация", "Нет игроков в сессии")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление персонажами игроков")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Список игроков с вкладками
        tabs = QTabWidget()
        
        for user_id, player in self.players.items():
            char_id = player.get('character_id')
            if not char_id:
                continue
            
            # Получаем полные данные персонажа
            character = self.get_character_data(char_id)
            if not character:
                continue
            
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            # Статистика
            stats_group = QGroupBox("Характеристики")
            stats_layout = QGridLayout()
            
            # Поля для редактирования
            fields = {
                'name': ('Имя', character.get('name', '')),
                'level': ('Уровень', character.get('level', 1)),
                'experience': ('Опыт', character.get('experience', 0)),
                'strength': ('Сила', character.get('strength', 10)),
                'dexterity': ('Ловкость', character.get('dexterity', 10)),
                'intelligence': ('Интеллект', character.get('intelligence', 10)),
                'charisma': ('Харизма', character.get('charisma', 10)),
                'current_hp': ('Текущее HP', character.get('current_hp', 10)),
                'max_hp': ('Макс. HP', character.get('max_hp', 10)),
                'current_mp': ('Текущая MP', character.get('current_mp', 5)),
                'max_mp': ('Макс. MP', character.get('max_mp', 5))
            }
            
            inputs = {}
            row = 0
            for key, (label, value) in fields.items():
                stats_layout.addWidget(QLabel(label), row, 0)
                input_field = QLineEdit(str(value))
                stats_layout.addWidget(input_field, row, 1)
                inputs[key] = input_field
                row += 1
            
            stats_group.setLayout(stats_layout)
            tab_layout.addWidget(stats_group)
            
            # Инвентарь
            inv_group = QGroupBox("Инвентарь")
            inv_layout = QVBoxLayout()
            inv_list = QListWidget()
            self.load_inventory_for_tab(char_id, inv_list)
            inv_layout.addWidget(inv_list)
            
            btn_layout = QHBoxLayout()
            add_item_btn = QPushButton("➕ Выдать предмет")
            add_item_btn.clicked.connect(lambda: self.add_item_to_character(char_id, inv_list))
            remove_item_btn = QPushButton("➖ Удалить предмет")
            remove_item_btn.clicked.connect(lambda: self.remove_item_from_character(char_id, inv_list))
            btn_layout.addWidget(add_item_btn)
            btn_layout.addWidget(remove_item_btn)
            inv_layout.addLayout(btn_layout)
            
            inv_group.setLayout(inv_layout)
            tab_layout.addWidget(inv_group)
            
            # Кнопка сохранения
            save_btn = QPushButton("💾 Сохранить изменения")
            save_btn.clicked.connect(lambda checked, cid=char_id, inp=inputs: self.save_character_stats(cid, inp))
            tab_layout.addWidget(save_btn)
            
            tab.setLayout(tab_layout)
            tabs.addTab(tab, f"{player['character_name']} ({player['username']})")
        
        layout.addWidget(tabs)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def save_character_stats(self, character_id, inputs):
        """Сохраняет изменённые характеристики персонажа"""
        updates = {}
        for key, widget in inputs.items():
            try:
                if key == 'name':
                    updates[key] = widget.text().strip()
                else:
                    updates[key] = int(widget.text())
            except ValueError:
                QMessageBox.warning(self, "Ошибка", f"Неверное значение для {key}")
                return
        
        if api_client.update_character(character_id, updates):
            QMessageBox.information(self, "Успех", "Характеристики обновлены")
            # Обновляем отображение в основном окне
            self.refresh_data()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить характеристики")
    
    def get_character_data(self, character_id):
        characters = api_client.get_my_characters(self.user_data['id'])
        for char in characters:
            if char['id'] == character_id:
                return char
        return {}
  
    def load_inventory_for_tab(self, character_id, list_widget):
        items = api_client.get_character_inventory(character_id)
        list_widget.clear()
        for item in items:
            item_data = item.get('item_data', {})
            name = item.get('custom_name') or item_data.get('name', '?')
            icon = item_data.get('icon', '📦')
            qty = f" x{item['quantity']}" if item['quantity'] > 1 else ""
            equipped = " ⚔️" if item.get('is_equipped') else ""
            list_widget.addItem(f"{icon} {name}{equipped}{qty}")
            list_widget.item(list_widget.count() - 1).setData(Qt.UserRole, item['item_id'])
    
    def update_character_stat(self, character_id, stat_name, value):
        api_client.update_character(character_id, {stat_name: value})
    
    def add_item_to_character(self, character_id, list_widget):
        items = api_client.get_all_items()
        if not items:
            QMessageBox.warning(self, "Нет предметов", "Нет доступных предметов для выдачи")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор предмета")
        dialog.setFixedSize(400, 500)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        item_list = QListWidget()
        for item in items:
            item_list.addItem(f"{item['icon']} {item['name']} - {item.get('description', '')}")
            item_list.item(item_list.count() - 1).setData(Qt.UserRole, item['id'])
        layout.addWidget(item_list)
        
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Количество:"))
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 99)
        qty_layout.addWidget(qty_spin)
        layout.addLayout(qty_layout)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Выдать")
        cancel_btn = QPushButton("Отмена")
        
        def on_add():
            current = item_list.currentItem()
            if current:
                item_id = current.data(Qt.UserRole)
                quantity = qty_spin.value()
                if api_client.add_item_to_character(character_id, item_id, quantity):
                    self.load_inventory_for_tab(character_id, list_widget)
                    dialog.accept()
        
        add_btn.clicked.connect(on_add)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def remove_item_from_character(self, character_id, list_widget):
        current = list_widget.currentItem()
        if not current:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для удаления")
            return
        
        item_id = current.data(Qt.UserRole)
        if api_client.remove_item_from_character(character_id, item_id):
            self.load_inventory_for_tab(character_id, list_widget)
    
    def show_items_management(self):
        """Управление глобальными предметами"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление предметами")
        dialog.setMinimumSize(600, 500)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Список предметов
        items_list = QListWidget()
        self.load_items_list(items_list)
        layout.addWidget(items_list)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("➕ Создать предмет")
        create_btn.clicked.connect(lambda: self.create_new_item(dialog, items_list))
        delete_btn = QPushButton("🗑 Удалить выбранный")
        delete_btn.clicked.connect(lambda: self.delete_selected_item(items_list))
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(lambda: self.load_items_list(items_list))
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def load_items_list(self, items_list):
        """Загружает список всех предметов в QListWidget"""
        items_list.clear()
        items = api_client.get_all_items()
        for item in items:
            text = f"{item['icon']} {item['name']} [{item['item_type']}]"
            if item.get('effects'):
                effects = ', '.join(f"{k}+{v}" for k,v in item['effects'].items())
                text += f" ({effects})"
            items_list.addItem(text)
            items_list.item(items_list.count()-1).setData(Qt.UserRole, item['id'])

    def create_new_item(self, parent, items_list):
        """Диалог создания нового предмета"""
        dialog = QDialog(parent)
        dialog.setWindowTitle("Создание предмета")
        dialog.setMinimumSize(400, 500)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Поля
        fields = {
            'name': ('Название', QLineEdit()),
            'description': ('Описание', QTextEdit()),
            'item_type': ('Тип', QComboBox()),
            'slot': ('Слот (для экипировки)', QLineEdit()),
            'icon': ('Иконка (эмодзи)', QLineEdit()),
            'is_equippable': ('Экипируемый', QComboBox()),
            'effects': ('Эффекты (JSON)', QTextEdit())
        }
        
        # Типы предметов
        fields['item_type'][1].addItems(['weapon', 'armor', 'consumable', 'accessory', 'misc'])
        
        # Экипируемый
        fields['is_equippable'][1].addItems(['Да', 'Нет'])
        
        # Эффекты по умолчанию
        fields['effects'][1].setPlaceholderText('{"strength": 2, "heal_hp": 10}')
        
        for label, widget in fields.values():
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("✅ Создать")
        cancel_btn = QPushButton("❌ Отмена")

    def delete_selected_item(self, items_list):
        """Удаляет выбранный предмет"""
        current = items_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для удаления")
            return
        item_id = current.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Подтверждение", "Удалить предмет? Это действие необратимо.",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if api_client.delete_item(item_id):
                QMessageBox.information(self, "Успех", "Предмет удалён")
                self.load_items_list(items_list)
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить предмет")
    
    def open_story_dialog(self):
        dialog = StoryDialog(api_client, self.user_data, self.session_data['id'], self)
        dialog.exec_()
    
    def add_game_object(self, obj_type):
        """Добавляет новый игровой объект (локацию, NPC, монстра)"""
        name, ok = QInputDialog.getText(self, f"Добавление {obj_type}", "Название:")
        if not ok or not name:
            return
        
        description, ok = QInputDialog.getText(self, f"Добавление {obj_type}", 
                                            f"Описание для '{name}':", 
                                            QInputDialog.MultiLine)
        if not ok:
            description = ""
        
        # Создаём через API
        context = api_client.create_context(
            session_id=self.session_data['id'],
            context_type=obj_type,
            name=name,
            description=description
        )
        if context:
            QMessageBox.information(self, "Успех", f"{obj_type.capitalize()} '{name}' добавлен")
            # Добавляем в локальные списки и UI
            if obj_type == 'location':
                self.game_objects['locations'].append(context)
                self.locations_list.addItem(f"📍 {name}")
            elif obj_type == 'npc':
                self.game_objects['npcs'].append(context)
                self.npcs_list.addItem(f"👤 {name}")
            elif obj_type == 'monster':
                self.game_objects['monsters'].append(context)
                self.monsters_list.addItem(f"👹 {name}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить объект")

    def edit_game_object(self, obj_type, item):
        """Редактирует существующий игровой объект"""
        obj = item.data(Qt.UserRole)
        if not obj:
            return
        
        name, ok = QInputDialog.getText(self, f"Редактирование {obj_type}", 
                                        "Новое название:", text=obj['name'])
        if ok and name:
            description, ok = QInputDialog.getText(self, f"Редактирование {obj_type}", 
                                                "Новое описание:", 
                                                QInputDialog.MultiLine,
                                                obj.get('description', ''))
            if not ok:
                description = obj.get('description', '')
            
            # Обновляем через API (сначала удалим старый, создадим новый - или добавить метод update_context)
            # Проще: удалить и создать заново
            if api_client.delete_context(obj['id']):
                new_context = api_client.create_context(
                    session_id=self.session_data['id'],
                    context_type=obj_type,
                    name=name,
                    description=description
                )
                if new_context:
                    QMessageBox.information(self, "Успех", f"{obj_type.capitalize()} обновлён")
                    # Обновляем локальные списки
                    self.load_game_objects()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось обновить объект")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить старую версию")
    
    def show_player_context_menu(self, position):
        item = self.players_list.itemAt(position)
        if not item:
            return
        
        user_id = item.data(Qt.UserRole)
        player = self.players.get(user_id)
        if not player:
            return
        
        menu = QMenu()
        
        view_stats = QAction("📊 Просмотреть статистику", self)
        view_stats.triggered.connect(lambda: self.view_player_stats(player))
        menu.addAction(view_stats)
        
        view_inv = QAction("📦 Просмотреть инвентарь", self)
        view_inv.triggered.connect(lambda: self.view_player_inventory(player))
        menu.addAction(view_inv)
        
        edit_stats = QAction("✏️ Редактировать статы", self)
        edit_stats.triggered.connect(lambda: self.edit_player_stats(player))
        menu.addAction(edit_stats)
        
        give_item = QAction("🎁 Выдать предмет", self)
        give_item.triggered.connect(lambda: self.give_item_to_player(player))
        menu.addAction(give_item)
        
        menu.exec_(self.players_list.mapToGlobal(position))

    def view_player_stats(self, player):
        character_id = player.get('character_id')
        if not character_id:
            QMessageBox.warning(self, "Ошибка", "У игрока нет персонажа")
            return
        character = self.get_character_data(character_id)
        if not character:
            return
        
        stats_text = f"""
        📛 Имя: {character.get('name')}
        ⭐ Уровень: {character.get('level')}
        📈 Опыт: {character.get('experience')}
        ❤️ HP: {character.get('current_hp')}/{character.get('max_hp')}
        💙 MP: {character.get('current_mp')}/{character.get('max_mp')}
        💪 Сила: {character.get('strength')}
        🏃 Ловкость: {character.get('dexterity')}
        🧠 Интеллект: {character.get('intelligence')}
        💬 Харизма: {character.get('charisma')}
        """
        QMessageBox.information(self, f"Статы {player['character_name']}", stats_text)

    def view_player_inventory(self, player):
        character_id = player.get('character_id')
        if not character_id:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Инвентарь {player['character_name']}")
        dialog.setMinimumSize(500, 400)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        inv_list = QListWidget()
        self.load_inventory_for_tab(character_id, inv_list)
        layout.addWidget(inv_list)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def edit_player_stats(self, player):
        character_id = player.get('character_id')
        if not character_id:
            return
        character = self.get_character_data(character_id)
        if not character:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Редактирование {player['character_name']}")
        dialog.setMinimumSize(400, 500)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Поля
        fields = {}
        stats = ['name', 'level', 'experience', 'strength', 'dexterity', 
                'intelligence', 'charisma', 'current_hp', 'max_hp', 
                'current_mp', 'max_mp']
        
        for stat in stats:
            layout.addWidget(QLabel(stat.capitalize()))
            widget = QLineEdit(str(character.get(stat, '')))
            layout.addWidget(widget)
            fields[stat] = widget
        
        def save():
            updates = {}
            for stat, widget in fields.items():
                value = widget.text().strip()
                if stat == 'name':
                    updates[stat] = value
                else:
                    try:
                        updates[stat] = int(value)
                    except ValueError:
                        QMessageBox.warning(dialog, "Ошибка", f"Неверное значение для {stat}")
                        return
            if api_client.update_character(character_id, updates):
                QMessageBox.information(dialog, "Успех", "Статы обновлены")
                dialog.accept()
                self.refresh_data()
            else:
                QMessageBox.warning(dialog, "Ошибка", "Не удалось обновить статы")
        
        save_btn = QPushButton("💾 Сохранить")
        save_btn.clicked.connect(save)
        layout.addWidget(save_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def give_item_to_player(self, player):
        character_id = player.get('character_id')
        if not character_id:
            return
        # Используем уже существующий метод add_item_to_character, но он требует list_widget.
        # Просто вызовем диалог выдачи без привязки к списку.
        items = api_client.get_all_items()
        if not items:
            QMessageBox.warning(self, "Нет предметов", "Нет доступных предметов для выдачи")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Выдача предмета {player['character_name']}")
        dialog.setFixedSize(400, 500)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        item_list = QListWidget()
        for item in items:
            item_list.addItem(f"{item['icon']} {item['name']} - {item.get('description', '')}")
            item_list.item(item_list.count()-1).setData(Qt.UserRole, item['id'])
        layout.addWidget(item_list)
        
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Количество:"))
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 99)
        qty_layout.addWidget(qty_spin)
        layout.addLayout(qty_layout)
        
        btn_layout = QHBoxLayout()
        give_btn = QPushButton("Выдать")
        cancel_btn = QPushButton("Отмена")
        
        def on_give():
            current = item_list.currentItem()
            if current:
                item_id = current.data(Qt.UserRole)
                quantity = qty_spin.value()
                if api_client.add_item_to_character(character_id, item_id, quantity):
                    QMessageBox.information(dialog, "Успех", "Предмет выдан")
                    dialog.accept()
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось выдать предмет")
        
        give_btn.clicked.connect(on_give)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(give_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()

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
        elif action_type == 'announcement':
            prefix = "📢 "
        elif action_type == 'combat':
            prefix = "⚔️ "
        elif action_type == 'dice':
            prefix = "🎲 "
        
        self.chat_display.append(f"[{timestamp}] {character}: {prefix}{message}")
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_players_list(self, data):
        print(f"[GM] on_players_list called with data: {data}")
        self.players_list.clear()
        self.players = {}
        
        for player in data.get('players', []):
            user_id = player['user_id']
            self.players[user_id] = player
            item = QListWidgetItem(f"🎮 {player['character_name']} (игрок: {player['username']})")
            item.setData(Qt.UserRole, user_id)
            self.players_list.addItem(item)
    
    def on_character_updated(self, data):
        self.log_text.append(f"📊 Обновлен персонаж ID {data['character_id']}: {data['updates']}")
    
    def on_item_added(self, data):
        self.log_text.append(f"📦 Добавлен предмет персонажу ID {data['character_id']}")
    
    def on_item_removed(self, data):
        self.log_text.append(f"🗑 Удален предмет у персонажа ID {data['character_id']}")
    
    def on_game_object_added(self, data):
        obj_type = data['type']
        name = data['name']
        self.log_text.append(f"📍 Добавлен {obj_type}: {name}")
        
        if obj_type == 'location':
            self.locations_list.addItem(f"📍 {name}")
        elif obj_type == 'npc':
            self.npcs_list.addItem(f"👤 {name}")
        elif obj_type == 'monster':
            self.monsters_list.addItem(f"👹 {name}")
    
    def on_player_joined(self, data):
        self.log_text.append(f"👤 Игрок {data['username']} ({data['character_name']}) присоединился")
        self.chat_display.append(f"📢 {data['character_name']} присоединился к сессии!")
        QTimer.singleShot(500, lambda: self.socket_client.get_players())
    
    def on_player_disconnected(self, data):
        self.log_text.append(f"👤 Игрок {data.get('user_id', '?')} отключился")
        QTimer.singleShot(500, lambda: self.socket_client.get_players())
    
    def send_message(self):
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
        
        self.socket_client.send_chat(message, action_map.get(action_type, "chat"))
        self.message_input.clear()
    
    def exit_session(self):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти из сессии?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.socket_client.reset()
            self.close()