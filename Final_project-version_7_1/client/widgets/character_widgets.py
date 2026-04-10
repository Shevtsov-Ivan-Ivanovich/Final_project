# client/widgets/character_widgets.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QGridLayout, QProgressBar,
                             QListWidget, QListWidgetItem, QDialog, QSpinBox,
                             QMessageBox, QInputDialog, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class CharacterStatsWidget(QWidget):
    """Виджет для отображения характеристик персонажа"""
    
    stats_updated = pyqtSignal(int, str, int)  # character_id, stat_name, value
    
    def __init__(self, character_data: dict, parent=None):
        super().__init__(parent)
        self.character_data = character_data
        self.is_editable = False
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        self.name_label = QLabel(self.character_data.get('name', 'Без имени'))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e67e22;")
        layout.addWidget(self.name_label)
        
        # Уровень и опыт
        level_frame = QFrame()
        level_frame.setStyleSheet("background-color: #3a3a3a; border-radius: 8px;")
        level_layout = QHBoxLayout()
        
        self.level_label = QLabel(f"⭐ Уровень: {self.character_data.get('level', 1)}")
        self.level_label.setStyleSheet("font-size: 14px; color: #f39c12;")
        level_layout.addWidget(self.level_label)
        
        self.exp_label = QLabel(f"📈 Опыт: {self.character_data.get('experience', 0)}")
        self.exp_label.setStyleSheet("font-size: 14px; color: #3498db;")
        level_layout.addWidget(self.exp_label)
        
        level_layout.addStretch()
        level_frame.setLayout(level_layout)
        layout.addWidget(level_frame)
        
        # HP
        hp_group = QGroupBox("❤️ Здоровье")
        hp_layout = QVBoxLayout()
        
        self.hp_label = QLabel(f"{self.character_data.get('current_hp', 10)} / {self.character_data.get('max_hp', 10)}")
        self.hp_label.setAlignment(Qt.AlignCenter)
        self.hp_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #e74c3c;")
        hp_layout.addWidget(self.hp_label)
        
        self.hp_bar = QProgressBar()
        hp_percent = (self.character_data.get('current_hp', 10) / self.character_data.get('max_hp', 10)) * 100
        self.hp_bar.setValue(int(hp_percent))
        self.hp_bar.setStyleSheet("QProgressBar::chunk { background-color: #e74c3c; }")
        hp_layout.addWidget(self.hp_bar)
        
        hp_group.setLayout(hp_layout)
        layout.addWidget(hp_group)
        
        # MP
        mp_group = QGroupBox("💙 Мана")
        mp_layout = QVBoxLayout()
        
        self.mp_label = QLabel(f"{self.character_data.get('current_mp', 5)} / {self.character_data.get('max_mp', 5)}")
        self.mp_label.setAlignment(Qt.AlignCenter)
        self.mp_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #3498db;")
        mp_layout.addWidget(self.mp_label)
        
        self.mp_bar = QProgressBar()
        mp_percent = (self.character_data.get('current_mp', 5) / self.character_data.get('max_mp', 5)) * 100
        self.mp_bar.setValue(int(mp_percent))
        self.mp_bar.setStyleSheet("QProgressBar::chunk { background-color: #3498db; }")
        mp_layout.addWidget(self.mp_bar)
        
        mp_group.setLayout(mp_layout)
        layout.addWidget(mp_group)
        
        # Атрибуты
        stats_group = QGroupBox("📊 Атрибуты")
        stats_layout = QGridLayout()
        
        self.stat_widgets = {}
        stats_data = [
            ('💪 Сила', 'strength', self.character_data.get('strength', 10)),
            ('🏃 Ловкость', 'dexterity', self.character_data.get('dexterity', 10)),
            ('🧠 Интеллект', 'intelligence', self.character_data.get('intelligence', 10)),
            ('💬 Харизма', 'charisma', self.character_data.get('charisma', 10))
        ]
        
        for i, (name, key, value) in enumerate(stats_data):
            row = i // 2
            col = i % 2 * 2
            
            label = QLabel(name)
            label.setStyleSheet("font-size: 12px; color: #bdc3c7;")
            stats_layout.addWidget(label, row, col)
            
            value_label = QLabel(str(value))
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
            stats_layout.addWidget(value_label, row, col + 1)
            self.stat_widgets[key] = value_label
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        self.setLayout(layout)
    
    def update_stats(self, character_data: dict):
        """Обновляет отображаемые характеристики"""
        self.character_data.update(character_data)
        
        # Обновляем имя
        if 'name' in character_data:
            self.name_label.setText(character_data['name'])
        
        # Обновляем уровень и опыт
        if 'level' in character_data:
            self.level_label.setText(f"⭐ Уровень: {character_data['level']}")
        if 'experience' in character_data:
            self.exp_label.setText(f"📈 Опыт: {character_data['experience']}")
        
        # Обновляем HP
        if 'current_hp' in character_data or 'max_hp' in character_data:
            current = character_data.get('current_hp', self.character_data.get('current_hp', 10))
            max_hp = character_data.get('max_hp', self.character_data.get('max_hp', 10))
            self.hp_label.setText(f"{current} / {max_hp}")
            self.hp_bar.setValue(int((current / max_hp) * 100))
        
        # Обновляем MP
        if 'current_mp' in character_data or 'max_mp' in character_data:
            current = character_data.get('current_mp', self.character_data.get('current_mp', 5))
            max_mp = character_data.get('max_mp', self.character_data.get('max_mp', 5))
            self.mp_label.setText(f"{current} / {max_mp}")
            self.mp_bar.setValue(int((current / max_mp) * 100))
        
        # Обновляем атрибуты
        for key, widget in self.stat_widgets.items():
            if key in character_data:
                widget.setText(str(character_data[key]))
                self.character_data[key] = character_data[key]
    
    def set_editable(self, editable: bool):
        """Устанавливает режим редактирования"""
        self.is_editable = editable


class CharacterSelectorWidget(QWidget):
    """Виджет для выбора персонажа из списка"""
    
    character_selected = pyqtSignal(dict)
    character_created = pyqtSignal(str)
    character_deleted = pyqtSignal(int)
    
    def __init__(self, api_client, user_id: int, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_id = user_id
        self.characters = []
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("🎭 Мои персонажи")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title)
        
        # Список персонажей
        self.characters_list = QListWidget()
        self.characters_list.itemClicked.connect(self.on_character_clicked)
        self.characters_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.characters_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.characters_list)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.create_btn = QPushButton("➕ Создать")
        self.create_btn.clicked.connect(self.create_character)
        btn_layout.addWidget(self.create_btn)
        
        self.delete_btn = QPushButton("🗑 Удалить")
        self.delete_btn.clicked.connect(self.delete_character)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_characters()
    
    def load_characters(self):
        """Загружает список персонажей"""
        self.characters = self.api_client.get_my_characters(self.user_id)
        self.characters_list.clear()
        
        for char in self.characters:
            session_info = ""
            if char.get('session_id'):
                session_info = f" [в игре]"
            
            item = QListWidgetItem(f"🎭 {char['name']} (Ур. {char.get('level', 1)}){session_info}")
            item.setData(Qt.UserRole, char['id'])
            
            # Подсвечиваем персонажей в игре
            if char.get('session_id'):
                item.setForeground(Qt.gray)
            
            self.characters_list.addItem(item)
    
    def on_character_clicked(self, item):
        """Обработчик выбора персонажа"""
        character_id = item.data(Qt.UserRole)
        character = next((c for c in self.characters if c['id'] == character_id), None)
        
        if character:
            self.selected_character = character
            self.delete_btn.setEnabled(not character.get('session_id'))  # Нельзя удалить если в игре
            self.character_selected.emit(character)
    
    def create_character(self):
        """Создает нового персонажа"""
        name, ok = QInputDialog.getText(self, "Создание персонажа", "Имя персонажа:")
        if ok and name:
            character = self.api_client.create_character(self.user_id, name)
            if character:
                self.character_created.emit(name)
                self.load_characters()
                QMessageBox.information(self, "Успех", f"Персонаж '{name}' создан!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось создать персонажа")
    
    def delete_character(self):
        """Удаляет выбранного персонажа"""
        if not hasattr(self, 'selected_character'):
            return
        
        char = self.selected_character
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить персонажа '{char['name']}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.api_client.delete_character(char['id']):
                self.character_deleted.emit(char['id'])
                self.load_characters()
                QMessageBox.information(self, "Успех", f"Персонаж '{char['name']}' удален!")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось удалить персонажа")
    
    def show_context_menu(self, position):
        """Показывает контекстное меню для персонажа"""
        item = self.characters_list.itemAt(position)
        if not item:
            return
        
        from PyQt5.QtWidgets import QMenu, QAction
        
        menu = QMenu()
        
        view_action = QAction("📊 Просмотреть", self)
        view_action.triggered.connect(lambda: self.on_character_clicked(item))
        menu.addAction(view_action)
        
        if not item.foreground() == Qt.gray:
            delete_action = QAction("🗑 Удалить", self)
            delete_action.triggered.connect(self.delete_character)
            menu.addAction(delete_action)
        
        menu.exec_(self.characters_list.mapToGlobal(position))
    
    def refresh(self):
        """Обновляет список персонажей"""
        self.load_characters()