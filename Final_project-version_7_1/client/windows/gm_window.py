# client/windows/gm_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSplitter, QListWidget,
                             QTextEdit, QLineEdit, QComboBox, QMessageBox,
                             QTabWidget, QGroupBox, QDialog, QInputDialog,
                             QListWidgetItem, QMenu, QAction, QScrollArea,
                             QGridLayout, QSpinBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from client.api_client import api_client
from client.socket_client import socket_client
from client.windows.story_dialog import StoryDialog


class GMWindow(QWidget):
    def __init__(self, user_data, session_data):
        super().__init__()
        self.user_data = user_data
        self.session_data = session_data
        self.players = {}  # user_id -> player_data
        self.game_objects = {'locations': [], 'npcs': [], 'monsters': []}
        
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
        
        # Информация о сессии
        info_label = QLabel(f"🎮 Сессия: {self.session_data['name']}")
        info_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e67e22;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Кнопки управления
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
    
    def create_left_panel(self):
        panel = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Кнопки управления
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
        
        # Логи действий
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
        
        # Верхний сплиттер (игроки и объекты)
        splitter = QSplitter(Qt.Vertical)
        
        # Игроки
        players_group = QGroupBox("Игроки в сессии")
        players_layout = QVBoxLayout()
        
        self.players_list = QListWidget()
        self.players_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.players_list.customContextMenuRequested.connect(self.show_player_context_menu)
        players_layout.addWidget(self.players_list)
        
        players_group.setLayout(players_layout)
        splitter.addWidget(players_group)
        
        # Игровые объекты
        objects_group = QGroupBox("Игровые объекты")
        objects_layout = QVBoxLayout()
        
        objects_tabs = QTabWidget()
        
        # Локации
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
        
        # NPC
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
        
        # Монстры
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
        
        # Чат
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMaximumHeight(200)
        self.chat_display.setStyleSheet("background-color: #2a2a2a;")
        layout.addWidget(self.chat_display)
        
        # Строка ввода
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
        # Подключаем сигналы
        socket_client.connected_signal.connect(self.on_socket_connected)
        socket_client.disconnected_signal.connect(self.on_socket_disconnected)
        socket_client.chat_signal.connect(self.on_chat_message)
        socket_client.players_list_signal.connect(self.on_players_list)
        socket_client.character_updated_signal.connect(self.on_character_updated)
        socket_client.item_added_signal.connect(self.on_item_added)
        socket_client.item_removed_signal.connect(self.on_item_removed)
        socket_client.game_object_added_signal.connect(self.on_game_object_added)
        socket_client.player_joined_signal.connect(self.on_player_joined)
        socket_client.player_disconnected_signal.connect(self.on_player_disconnected)
    
    def connect_to_session(self):
        """Подключается к сессии как ГМ"""
        # Используем network_config для получения адреса сервера
        from client.network_config import network_config
        
        server_ip = network_config.host
        server_port = network_config.port
        
        print(f"Using server: {server_ip}:{server_port}")
        
        # Подключаемся к серверу
        if not socket_client.is_connected:
            if not socket_client.connect_to_server(server_ip, server_port):
                QMessageBox.warning(self, "Ошибка", 
                                   f"Не удалось подключиться к серверу {server_ip}:{server_port}\n"
                                   "Проверьте что сервер запущен и настройки верны")
                return
        
        # Регистрируемся как ГМ
        socket_client.register_gm(
            self.session_data['id'],
            self.user_data['id'],
            self.user_data['username']
        )
        
        # Загружаем игроков
        QTimer.singleShot(500, lambda: socket_client.get_players())
        
        # Загружаем логи
        self.load_logs()

    def load_logs(self):
        logs = api_client.get_session_logs(self.session_data['id'])
        for log in logs[:50]:  # Последние 50
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
        socket_client.get_players()
        self.load_logs()
    
    def show_players_management(self):
        """Показывает окно управления персонажами игроков"""
        if not self.players:
            QMessageBox.warning(self, "Нет игроков", "В сессии нет игроков")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление персонажами игроков")
        dialog.setMinimumSize(800, 600)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Список игроков с вкладками
        tabs = QTabWidget()
        
        for user_id, player in self.players.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            
            # Информация об игроке
            info_frame = QFrame()
            info_layout = QHBoxLayout()
            info_layout.addWidget(QLabel(f"👤 Игрок: {player['username']}"))
            info_layout.addWidget(QLabel(f"🎭 Персонаж: {player['character_name']}"))
            info_layout.addStretch()
            info_frame.setLayout(info_layout)
            tab_layout.addWidget(info_frame)
            
            # Характеристики
            stats_frame = QGroupBox("Характеристики")
            stats_layout = QGridLayout()
            
            # Загружаем текущие характеристики персонажа
            character_data = self.get_character_data(player['character_id'])
            
            stats = [
                ('❤️ HP', 'current_hp', character_data.get('current_hp', 10), character_data.get('max_hp', 10)),
                ('💙 MP', 'current_mp', character_data.get('current_mp', 5), character_data.get('max_mp', 5)),
                ('💪 Сила', 'strength', character_data.get('strength', 10)),
                ('🏃 Ловкость', 'dexterity', character_data.get('dexterity', 10)),
                ('🧠 Интеллект', 'intelligence', character_data.get('intelligence', 10)),
                ('💬 Харизма', 'charisma', character_data.get('charisma', 10)),
                ('⭐ Уровень', 'level', character_data.get('level', 1)),
                ('📈 Опыт', 'experience', character_data.get('experience', 0))
            ]
            
            self.stat_widgets = {}
            
            for i, (label, key, value, *max_val) in enumerate(stats):
                row = i // 2
                col = i % 2 * 2
                
                stats_layout.addWidget(QLabel(label), row, col)
                
                if 'hp' in key.lower() and max_val:
                    # HP/MP с ползунком
                    widget = QWidget()
                    widget_layout = QHBoxLayout()
                    spinbox = QSpinBox()
                    spinbox.setRange(0, max_val[0])
                    spinbox.setValue(value)
                    spinbox.valueChanged.connect(lambda v, k=key, cid=player['character_id']: 
                                                  self.update_character_stat(cid, k, v))
                    widget_layout.addWidget(spinbox)
                    widget_layout.addWidget(QLabel(f"/ {max_val[0]}"))
                    widget.setLayout(widget_layout)
                    stats_layout.addWidget(widget, row, col + 1)
                    self.stat_widgets[f"{player['character_id']}_{key}"] = spinbox
                else:
                    spinbox = QSpinBox()
                    spinbox.setRange(0, 99)
                    spinbox.setValue(value)
                    spinbox.valueChanged.connect(lambda v, k=key, cid=player['character_id']: 
                                                  self.update_character_stat(cid, k, v))
                    stats_layout.addWidget(spinbox, row, col + 1)
                    self.stat_widgets[f"{player['character_id']}_{key}"] = spinbox
            
            stats_frame.setLayout(stats_layout)
            tab_layout.addWidget(stats_frame)
            
            # Инвентарь
            inv_frame = QGroupBox("Инвентарь")
            inv_layout = QVBoxLayout()
            
            inv_list = QListWidget()
            self.load_inventory_for_tab(player['character_id'], inv_list)
            inv_layout.addWidget(inv_list)
            
            # Кнопки управления инвентарем
            inv_buttons = QHBoxLayout()
            
            add_item_btn = QPushButton("➕ Добавить предмет")
            add_item_btn.clicked.connect(lambda: self.add_item_to_character(player['character_id'], inv_list))
            inv_buttons.addWidget(add_item_btn)
            
            remove_item_btn = QPushButton("➖ Удалить предмет")
            remove_item_btn.clicked.connect(lambda: self.remove_item_from_character(player['character_id'], inv_list))
            inv_buttons.addWidget(remove_item_btn)
            
            inv_layout.addLayout(inv_buttons)
            inv_frame.setLayout(inv_layout)
            tab_layout.addWidget(inv_frame)
            
            tab.setLayout(tab_layout)
            tabs.addTab(tab, player['character_name'])
        
        layout.addWidget(tabs)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
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
            # Сохраняем ID предмета
            list_widget.item(list_widget.count() - 1).setData(Qt.UserRole, item['item_id'])
    
    def update_character_stat(self, character_id, stat_name, value):
        socket_client.gm_update_character(character_id, {stat_name: value})
    
    def add_item_to_character(self, character_id, list_widget):
        # Получаем список всех предметов
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
        
        # Выбор количества
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
                socket_client.gm_add_item(character_id, item_id, quantity)
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
        socket_client.gm_remove_item(character_id, item_id)
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
        items = api_client.get_all_items()
        for item in items:
            items_list.addItem(f"{item['icon']} {item['name']} - {item.get('description', '')} (Тип: {item['item_type']})")
            items_list.item(items_list.count() - 1).setData(Qt.UserRole, item['id'])
        layout.addWidget(items_list)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Добавить предмет")
        add_btn.clicked.connect(lambda: self.create_new_item(dialog, items_list))
        btn_layout.addWidget(add_btn)
        
        delete_btn = QPushButton("🗑 Удалить предмет")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(lambda: self.delete_selected_item(items_list))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def create_new_item(self, parent, items_list):
        dialog = QDialog(parent)
        dialog.setWindowTitle("Создание предмета")
        dialog.setFixedSize(400, 500)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Название
        layout.addWidget(QLabel("Название:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        # Описание
        layout.addWidget(QLabel("Описание:"))
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(100)
        layout.addWidget(desc_input)
        
        # Тип
        layout.addWidget(QLabel("Тип:"))
        type_combo = QComboBox()
        type_combo.addItems(['weapon', 'armor', 'consumable', 'misc'])
        layout.addWidget(type_combo)
        
        # Слот
        layout.addWidget(QLabel("Слот (для экипировки):"))
        slot_combo = QComboBox()
        slot_combo.addItems(['', 'head', 'body', 'hands', 'feet', 'weapon', 'shield', 'finger', 'neck'])
        layout.addWidget(slot_combo)
        
        # Иконка
        layout.addWidget(QLabel("Иконка (emoji):"))
        icon_input = QLineEdit()
        icon_input.setText("📦")
        layout.addWidget(icon_input)
        
        # Эффекты
        layout.addWidget(QLabel("Эффекты (JSON):"))
        effects_input = QTextEdit()
        effects_input.setPlaceholderText('{"strength": 2, "dexterity": 1}')
        effects_input.setMaximumHeight(80)
        layout.addWidget(effects_input)
        
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Создать")
        cancel_btn = QPushButton("Отмена")
        
        def on_create():
            try:
                effects = {}
                if effects_input.toPlainText().strip():
                    import json
                    effects = json.loads(effects_input.toPlainText())
                
                item = api_client.create_item(
                    name=name_input.text(),
                    description=desc_input.toPlainText(),
                    item_type=type_combo.currentText(),
                    slot=slot_combo.currentText() or None,
                    icon=icon_input.text(),
                    effects=effects
                )
                if item:
                    QMessageBox.information(dialog, "Успех", "Предмет создан")
                    dialog.accept()
                    # Обновляем список
                    items_list.clear()
                    new_items = api_client.get_all_items()
                    for it in new_items:
                        items_list.addItem(f"{it['icon']} {it['name']} - {it.get('description', '')}")
                        items_list.item(items_list.count() - 1).setData(Qt.UserRole, it['id'])
                else:
                    QMessageBox.warning(dialog, "Ошибка", "Не удалось создать предмет")
            except Exception as e:
                QMessageBox.warning(dialog, "Ошибка", f"Ошибка: {e}")
        
        create_btn.clicked.connect(on_create)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def delete_selected_item(self, items_list):
        current = items_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для удаления")
            return
        
        reply = QMessageBox.question(self, "Подтверждение", 
                                     "Удалить этот предмет? Все экземпляры у игроков будут удалены.",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            item_id = current.data(Qt.UserRole)
            if api_client.delete_item(item_id):
                QMessageBox.information(self, "Успех", "Предмет удален")
                items_list.takeItem(items_list.row(current))
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить предмет")
    
    def open_story_dialog(self):
        dialog = StoryDialog(api_client, self.user_data, self.session_data['id'], self)
        dialog.exec_()
    
    def add_game_object(self, obj_type):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Добавление {obj_type}")
        dialog.setFixedSize(400, 400)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Название:"))
        name_input = QLineEdit()
        layout.addWidget(name_input)
        
        layout.addWidget(QLabel("Описание:"))
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(150)
        layout.addWidget(desc_input)
        
        layout.addWidget(QLabel("Дополнительные данные (JSON):"))
        data_input = QTextEdit()
        data_input.setPlaceholderText('{"health": 50, "damage": 10}')
        data_input.setMaximumHeight(100)
        layout.addWidget(data_input)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        cancel_btn = QPushButton("Отмена")
        
        def on_add():
            name = name_input.text()
            if not name:
                QMessageBox.warning(dialog, "Ошибка", "Введите название")
                return
            
            try:
                data = {}
                if data_input.toPlainText().strip():
                    import json
                    data = json.loads(data_input.toPlainText())
            except:
                pass
            
            context = api_client.create_context(
                self.session_data['id'],
                obj_type,
                name,
                desc_input.toPlainText(),
                data
            )
            
            if context:
                if obj_type == 'location':
                    self.game_objects['locations'].append(context)
                    self.locations_list.addItem(f"📍 {name}")
                elif obj_type == 'npc':
                    self.game_objects['npcs'].append(context)
                    self.npcs_list.addItem(f"👤 {name}")
                elif obj_type == 'monster':
                    self.game_objects['monsters'].append(context)
                    self.monsters_list.addItem(f"👹 {name}")
                
                socket_client.add_game_object(obj_type, name, desc_input.toPlainText(), data)
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Ошибка", "Не удалось добавить объект")
        
        add_btn.clicked.connect(on_add)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def edit_game_object(self, obj_type, item):
        # Получаем ID объекта
        name = item.text()[2:]  # Убираем эмодзи
        obj = None
        if obj_type == 'location':
            obj = next((o for o in self.game_objects['locations'] if o['name'] == name), None)
        elif obj_type == 'npc':
            obj = next((o for o in self.game_objects['npcs'] if o['name'] == name), None)
        elif obj_type == 'monster':
            obj = next((o for o in self.game_objects['monsters'] if o['name'] == name), None)
        
        if obj:
            QMessageBox.information(self, "Информация", 
                                   f"Объект: {obj['name']}\nОписание: {obj['description']}\n"
                                   f"Данные: {obj.get('data', {})}")
    
    def show_player_context_menu(self, position):
        item = self.players_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        view_stats_action = QAction("📊 Смотреть статистику", self)
        view_stats_action.triggered.connect(lambda: self.view_player_stats(item))
        menu.addAction(view_stats_action)
        
        view_inv_action = QAction("📦 Смотреть инвентарь", self)
        view_inv_action.triggered.connect(lambda: self.view_player_inventory(item))
        menu.addAction(view_inv_action)
        
        edit_stats_action = QAction("✏️ Редактировать характеристики", self)
        edit_stats_action.triggered.connect(lambda: self.edit_player_stats(item))
        menu.addAction(edit_stats_action)
        
        give_item_action = QAction("🎁 Выдать предмет", self)
        give_item_action.triggered.connect(lambda: self.give_item_to_player(item))
        menu.addAction(give_item_action)
        
        menu.exec_(self.players_list.mapToGlobal(position))
    
    def view_player_stats(self, item):
        user_id = item.data(Qt.UserRole)
        player = self.players.get(user_id)
        if player:
            character_data = self.get_character_data(player['character_id'])
            QMessageBox.information(self, f"Статистика {player['character_name']}",
                                   f"Уровень: {character_data.get('level', 1)}\n"
                                   f"❤️ HP: {character_data.get('current_hp', 10)}/{character_data.get('max_hp', 10)}\n"
                                   f"💙 MP: {character_data.get('current_mp', 5)}/{character_data.get('max_mp', 5)}\n"
                                   f"💪 Сила: {character_data.get('strength', 10)}\n"
                                   f"🏃 Ловкость: {character_data.get('dexterity', 10)}\n"
                                   f"🧠 Интеллект: {character_data.get('intelligence', 10)}\n"
                                   f"💬 Харизма: {character_data.get('charisma', 10)}")
    
    def view_player_inventory(self, item):
        user_id = item.data(Qt.UserRole)
        player = self.players.get(user_id)
        if player:
            items = api_client.get_character_inventory(player['character_id'])
            if not items:
                QMessageBox.information(self, "Инвентарь", "Инвентарь пуст")
                return
            
            text = "Инвентарь:\n\n"
            for inv_item in items:
                item_data = inv_item.get('item_data', {})
                name = inv_item.get('custom_name') or item_data.get('name', '?')
                icon = item_data.get('icon', '📦')
                qty = f" x{inv_item['quantity']}" if inv_item['quantity'] > 1 else ""
                text += f"{icon} {name}{qty}\n"
            
            QMessageBox.information(self, f"Инвентарь {player['character_name']}", text)
    
    def edit_player_stats(self, item):
        user_id = item.data(Qt.UserRole)
        player = self.players.get(user_id)
        if player:
            self.show_players_management()  # Открываем полное окно управления
    
    def give_item_to_player(self, item):
        user_id = item.data(Qt.UserRole)
        player = self.players.get(user_id)
        if player:
            self.add_item_to_character(player['character_id'], None)
    
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
        
        # Прокручиваем вниз
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_players_list(self, data):
        self.players_list.clear()
        self.players = {}
        
        for player in data.get('players', []):
            user_id = player['user_id']
            self.players[user_id] = player
            
            ping = player.get('ping', 0)
            ping_text = f" ({ping}ms)" if ping else ""
            item = QListWidgetItem(f"🎮 {player['character_name']} (игрок: {player['username']}){ping_text}")
            item.setData(Qt.UserRole, user_id)
            self.players_list.addItem(item)
    
    def on_character_updated(self, data):
        character_id = data['character_id']
        updates = data['updates']
        # Обновляем UI при необходимости
        self.log_text.append(f"📊 Обновлен персонаж ID {character_id}: {updates}")
    
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
        socket_client.get_players()
    
    def on_player_disconnected(self, data):
        self.log_text.append(f"👤 Игрок {data.get('user_id', '?')} отключился")
        socket_client.get_players()
    
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
        
        socket_client.send_chat(message, action_map.get(action_type, "chat"))
        self.message_input.clear()
    
    def exit_session(self):
        reply = QMessageBox.question(self, "Выход", "Вы уверены, что хотите выйти из сессии?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            socket_client.disconnect()
            self.close()