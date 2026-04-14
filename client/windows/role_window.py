# client/windows/role_window.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QDialog, QListWidget,
                             QInputDialog, QRadioButton, QButtonGroup, QGroupBox,
                             QMenu, QAction, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from client.api_client import api_client
from client.socket_client import SocketClient
from client.windows.gm_window import GMWindow
from client.windows.player_window import PlayerWindow


class RoleWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.player_window = None
        self.gm_window = None
        self.initUI()
        self.socket_client = SocketClient()
        print(f"[ROLE] RoleWindow created for user: {user_data.get('username')}")
    
    def initUI(self):
        self.setWindowTitle("ДПЖ - Выбор роли")
        self.setFixedSize(350, 250)
        self.setStyleSheet("""
            QWidget {
                background-color: #3a3a3a;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #5a5a5a;
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Выберите роль")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title)
        
        user_label = QLabel(f"Пользователь: {self.user_data['username']}")
        user_label.setAlignment(Qt.AlignCenter)
        user_label.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(user_label)
        
        layout.addSpacing(10)
        
        self.gm_btn = QPushButton("🎮 Гейм Мастер")
        self.gm_btn.clicked.connect(self.select_gm)
        layout.addWidget(self.gm_btn)
        
        self.player_btn = QPushButton("🎲 Игрок")
        self.player_btn.clicked.connect(self.select_player)
        layout.addWidget(self.player_btn)
        
        self.setLayout(layout)
    
    def select_gm(self):
        print(f"[ROLE] Selecting GM role for user {self.user_data['id']}")
        
        reply = QMessageBox.question(
            self, 
            "Выбор действия",
            "Что вы хотите сделать?\n\nДа - создать новую сессию\nНет - выбрать существующую",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Cancel:
            return
        elif reply == QMessageBox.Yes:
            self.create_session_and_continue()
            return
        
        sessions = api_client.get_my_sessions(self.user_data['id'])
        print(f"[ROLE] My sessions: {sessions}")
        
        if not sessions:
            reply = QMessageBox.question(self, "Нет сессий", 
                                        "У вас нет созданных сессий. Создать новую?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.create_session_and_continue()
            return
        
        self.show_session_selection(sessions, is_gm=True)

    def select_player(self):
        print(f"[ROLE] Selecting Player role for user {self.user_data['id']}")
        self.show_character_manager()
    
    def create_session_and_continue(self):
        name, ok = QInputDialog.getText(self, "Создание сессии", "Название сессии:")
        if ok and name:
            print(f"[ROLE] Creating session: {name}")
            session = api_client.create_session(name, self.user_data['id'])
            if session:
                QMessageBox.information(self, "Успех", f"Сессия '{name}' создана!")
                print(f"[ROLE] Session created: {session}")
                self.gm_window = GMWindow(self.user_data, session)
                self.gm_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать сессию")
    
    def show_session_selection(self, sessions, is_gm=False):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор сессии")
        dialog.setFixedSize(350, 400)
        dialog.setStyleSheet("""
            QDialog { background-color: #3a3a3a; }
            QLabel { color: #e0e0e0; }
            QListWidget { background-color: #4a4a4a; color: #e0e0e0; border: none; border-radius: 6px; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #e67e22; }
            QPushButton { background-color: #5a5a5a; border: none; border-radius: 6px; padding: 8px; color: white; }
            QPushButton:hover { background-color: #6a6a6a; }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        label = QLabel("Выберите сессию:")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        list_widget = QListWidget()
        for session in sessions:
            list_widget.addItem(f"{session['name']} (ID: {session['id']})")
            list_widget.item(list_widget.count() - 1).setData(Qt.UserRole, session['id'])
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("Выбрать")
        cancel_btn = QPushButton("Отмена")
        
        def on_select():
            current = list_widget.currentItem()
            if current:
                session_id = current.data(Qt.UserRole)
                session = next((s for s in sessions if s['id'] == session_id), None)
                if session:
                    print(f"[ROLE] Selected session: {session}")
                    dialog.accept()
                    if is_gm:
                        print(f"[ROLE] Opening GM window")
                        self.gm_window = GMWindow(self.user_data, session)
                        self.gm_window.show()
                        self.close()
        
        select_btn.clicked.connect(on_select)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_character_manager(self):
        """Показывает менеджер персонажей с возможностью удаления"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Управление персонажами")
        dialog.setMinimumSize(500, 500)
        dialog.setStyleSheet("""
            QDialog { background-color: #3a3a3a; }
            QLabel { color: #e0e0e0; font-size: 14px; font-weight: bold; }
            QListWidget { background-color: #4a4a4a; color: #e0e0e0; border: none; border-radius: 6px; }
            QListWidget::item { padding: 10px; }
            QListWidget::item:selected { background-color: #e67e22; }
            QListWidget::item:hover { background-color: #5a5a5a; }
            QPushButton { background-color: #5a5a5a; border: none; border-radius: 6px; padding: 10px; color: white; font-weight: bold; }
            QPushButton:hover { background-color: #6a6a6a; }
            QPushButton#delete { background-color: #8b3a3a; }
            QPushButton#delete:hover { background-color: #a04040; }
            QPushButton#play { background-color: #2d6a4f; }
            QPushButton#play:hover { background-color: #40916c; }
            QGroupBox { color: #e0e0e0; border: 1px solid #5a5a5a; border-radius: 8px; margin-top: 10px; }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("🎭 Мои персонажи")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; color: #e67e22;")
        layout.addWidget(title)
        
        info_label = QLabel("⚠️ Персонажи, отмеченные красным, уже используются в другой сессии. Подключение к новой сессии отключит их от текущей.")
        info_label.setStyleSheet("color: #f39c12; font-size: 11px; margin: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Список персонажей
        self.char_list = QListWidget()
        self.char_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.char_list.customContextMenuRequested.connect(lambda pos: self.show_char_context_menu(pos, self.char_list))
        layout.addWidget(self.char_list)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        create_btn = QPushButton("➕ Создать персонажа")
        create_btn.clicked.connect(lambda: self.create_new_character(dialog))
        btn_layout.addWidget(create_btn)
        
        delete_btn = QPushButton("🗑 Удалить")
        delete_btn.setObjectName("delete")
        delete_btn.clicked.connect(lambda: self.delete_selected_character(dialog))
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        # Группа подключения к сессии
        session_group = QGroupBox("Подключение к сессии")
        session_layout = QVBoxLayout()
        
        self.session_list = QListWidget()
        self.session_list.setMaximumHeight(150)
        session_layout.addWidget(self.session_list)
        
        play_btn = QPushButton("🎮 Играть выбранным персонажем")
        play_btn.setObjectName("play")
        play_btn.clicked.connect(lambda: self.play_with_selected(dialog))
        session_layout.addWidget(play_btn)
        
        session_group.setLayout(session_layout)
        layout.addWidget(session_group)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        
        # Загружаем данные
        self.load_characters()
        self.load_available_sessions()
        
        dialog.exec_()
    
    def load_characters(self):
        """Загружает список персонажей с информацией о привязке"""
        characters = api_client.get_my_characters(self.user_data['id'])
        self.char_list.clear()
        self.characters_data = characters
        
        # Получаем все сессии для отображения названий
        all_sessions = api_client.get_all_sessions()
        sessions_dict = {s['id']: s['name'] for s in all_sessions}
        
        for char in characters:
            session_info = ""
            is_attached = char.get('session_id') is not None
            
            if is_attached:
                session_name = sessions_dict.get(char['session_id'], 'неизвестная')
                session_info = f" 🔗 [играет в: {session_name}]"
            
            item_text = f"🎭 {char['name']} (Ур. {char.get('level', 1)}){session_info}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, char['id'])
            
            if is_attached:
                # Красный цвет для персонажей, которые уже в игре
                item.setForeground(Qt.red)
                item.setToolTip(f"ВНИМАНИЕ! Персонаж уже используется в сессии '{session_name}'. Подключение к другой сессии отключит его от текущей.")
            else:
                item.setForeground(Qt.white)
                item.setToolTip("Персонаж свободен")
            
            self.char_list.addItem(item)
        
        print(f"[ROLE] Loaded {len(characters)} characters")

    def load_available_sessions(self):
        """Загружает доступные сессии"""
        self.session_list.clear()
        self.sessions_data = api_client.get_all_sessions()
        
        if not self.sessions_data:
            self.session_list.addItem("❌ Нет доступных сессий")
            self.session_list.setEnabled(False)
            return
        
        for session in self.sessions_data:
            if session.get('is_active', True):
                item_text = f"🎮 {session['name']} (Мастер: {session.get('master_name', '?')})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, session['id'])
                self.session_list.addItem(item)
        
        if self.session_list.count() == 0:
            self.session_list.addItem("❌ Нет активных сессий")
            self.session_list.setEnabled(False)
    
    def create_new_character(self, parent_dialog):
        """Создает нового персонажа"""
        name, ok = QInputDialog.getText(self, "Создание персонажа", "Имя персонажа:")
        if ok and name:
            character = api_client.create_character(self.user_data['id'], name)
            if character:
                QMessageBox.information(self, "Успех", f"Персонаж '{name}' создан!")
                self.load_characters()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать персонажа")
    
    def delete_selected_character(self, parent_dialog):
        """Удаляет выбранного персонажа"""
        current = self.char_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Ошибка", "Выберите персонажа для удаления")
            return
        
        char_id = current.data(Qt.UserRole)
        char = next((c for c in self.characters_data if c['id'] == char_id), None)
        
        if not char:
            return
        
        # Проверяем, привязан ли персонаж к сессии
        if char.get('session_id'):
            reply = QMessageBox.question(
                self, 
                "Подтверждение",
                f"Персонаж '{char['name']}' привязан к сессии.\n\n"
                "При удалении он будет откреплён от сессии.\n"
                "Продолжить?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение", 
            f"Удалить персонажа '{char['name']}'?\nЭто действие необратимо.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Если персонаж в сессии, открепляем
            if char.get('session_id'):
                api_client.detach_character_from_session(char['id'])
                api_client.leave_session(char['session_id'], self.user_data['id'])
            
            if api_client.delete_character(char['id']):
                QMessageBox.information(self, "Успех", f"Персонаж '{char['name']}' удалён!")
                self.load_characters()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить персонажа")
    
    def show_char_context_menu(self, position, list_widget):
        """Показывает контекстное меню для персонажа"""
        item = list_widget.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        char_id = item.data(Qt.UserRole)
        char = next((c for c in self.characters_data if c['id'] == char_id), None)
        
        if char:
            info_action = QAction("📊 Информация", self)
            info_action.triggered.connect(lambda: self.show_char_info(char))
            menu.addAction(info_action)
            
            menu.addSeparator()
            
            if char.get('session_id'):
                reconnect_action = QAction("🔄 Подключиться заново", self)
                reconnect_action.triggered.connect(lambda: self.reconnect_character(char))
                menu.addAction(reconnect_action)
                
                detach_action = QAction("🔓 Открепить от сессии", self)
                detach_action.triggered.connect(lambda: self.detach_character(char))
                menu.addAction(detach_action)
            
            menu.addSeparator()
            
            delete_action = QAction("🗑 Удалить", self)
            delete_action.triggered.connect(lambda: self.delete_selected_character(None))
            menu.addAction(delete_action)
        
        menu.exec_(list_widget.mapToGlobal(position))
    
    def show_char_info(self, character):
        """Показывает информацию о персонаже"""
        QMessageBox.information(
            self,
            f"Информация о персонаже",
            f"📛 Имя: {character['name']}\n"
            f"⭐ Уровень: {character.get('level', 1)}\n"
            f"📈 Опыт: {character.get('experience', 0)}\n"
            f"❤️ HP: {character.get('current_hp', 10)}/{character.get('max_hp', 10)}\n"
            f"💙 MP: {character.get('current_mp', 5)}/{character.get('max_mp', 5)}\n"
            f"💪 Сила: {character.get('strength', 10)}\n"
            f"🏃 Ловкость: {character.get('dexterity', 10)}\n"
            f"🧠 Интеллект: {character.get('intelligence', 10)}\n"
            f"💬 Харизма: {character.get('charisma', 10)}\n"
            f"\n🔗 Привязан к сессии: {'Да' if character.get('session_id') else 'Нет'}"
        )
    
    def detach_character(self, character):
        """Открепляет персонажа от сессии"""
        if character.get('session_id'):
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Открепить персонажа '{character['name']}' от сессии?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                api_client.detach_character_from_session(character['id'])
                api_client.leave_session(character['session_id'], self.user_data['id'])
                QMessageBox.information(self, "Успех", f"Персонаж '{character['name']}' откреплён!")
                self.load_characters()

    def reconnect_character(self, character):
        """Переподключает персонажа к его сессии"""
        if not character.get('session_id'):
            QMessageBox.warning(self, "Ошибка", "Персонаж не привязан ни к какой сессии")
            return
        
        # Находим сессию
        session = next((s for s in api_client.get_all_sessions() if s['id'] == character['session_id']), None)
        
        if not session:
            QMessageBox.warning(self, "Ошибка", "Сессия не найдена")
            return
        
        if not session.get('is_active', True):
            QMessageBox.warning(self, "Ошибка", "Сессия не активна")
            return
        
        from client.socket_client import SocketClient
        from client.config_manager import config_manager
        
        socket_client = SocketClient()
        socket_client.base_url = f"http://{config_manager.host}:{config_manager.port}"
        
        # ИСПРАВЛЕНО: используем connect_player вместо register_player
        result = socket_client.connect_player(
            session['id'],
            self.user_data['id'],
            self.user_data['username'],
            character['id'],
            character['name']
        )
        
        if result:
            api_client.join_session(session['id'], self.user_data['id'])
            self.player_window = PlayerWindow(self.user_data, session, character)
            self.player_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось подключиться к сессии")

    def play_with_selected(self, parent_dialog):
        """Играет выбранным персонажем"""
        current_char = self.char_list.currentItem()
        if not current_char:
            QMessageBox.warning(self, "Ошибка", "Выберите персонажа")
            return
        
        char_id = current_char.data(Qt.UserRole)
        character = next((c for c in self.characters_data if c['id'] == char_id), None)
        
        if not character:
            QMessageBox.warning(self, "Ошибка", "Персонаж не найден")
            return
        
        current_session = self.session_list.currentItem()
        if not current_session:
            QMessageBox.warning(self, "Ошибка", "Выберите сессию")
            return
        
        session_id = current_session.data(Qt.UserRole)
        session = next((s for s in self.sessions_data if s['id'] == session_id), None)
        
        if not session:
            QMessageBox.warning(self, "Ошибка", "Сессия не найдена")
            return
        
        # Обновляем привязку персонажа в БД
        print(f"[ROLE] Updating character {character['id']} session to {session_id}")
        api_client.update_character_session(character['id'], session_id)
        
        # Присоединяемся к сессии
        api_client.join_session(session_id, self.user_data['id'])
        
        parent_dialog.accept()
        
        # Открываем окно игрока (PlayerWindow сам создаст свой экземпляр SocketClient)
        print(f"[ROLE] Opening PlayerWindow")
        self.player_window = PlayerWindow(self.user_data, session, character)
        self.player_window.show()
        self.close()