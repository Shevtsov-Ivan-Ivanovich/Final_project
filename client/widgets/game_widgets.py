# client/widgets/game_widgets.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QGroupBox, QFrame, QProgressBar, QGridLayout,
                             QDialog, QTextEdit, QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer


class PlayersListWidget(QWidget):
    """Виджет для отображения списка игроков (для ГМ)"""
    
    player_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.players = {}
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("👥 Игроки в сессии")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: #2ecc71;")
        layout.addWidget(title)
        
        self.players_list = QListWidget()
        self.players_list.itemClicked.connect(self.on_player_clicked)
        self.players_list.setContextMenuPolicy(Qt.CustomContextMenu)
        layout.addWidget(self.players_list)
        
        self.setLayout(layout)
    
    def update_players(self, players: list):
        """Обновляет список игроков"""
        self.players_list.clear()
        self.players = {}
        
        for player in players:
            user_id = player['user_id']
            self.players[user_id] = player
            
            ping = player.get('ping', 0)
            ping_text = f" ({ping}ms)" if ping else ""
            ping_color = "#2ecc71" if ping < 100 else "#f39c12" if ping < 200 else "#e74c3c"
            
            item = QListWidgetItem(f"🎮 {player['character_name']} (игрок: {player['username']}){ping_text}")
            item.setData(Qt.UserRole, user_id)
            item.setForeground(Qt.white)
            self.players_list.addItem(item)
    
    def on_player_clicked(self, item):
        """Обработчик выбора игрока"""
        user_id = item.data(Qt.UserRole)
        if user_id in self.players:
            self.player_selected.emit(self.players[user_id])
    
    def get_selected_player(self):
        """Возвращает выбранного игрока"""
        current = self.players_list.currentItem()
        if current:
            user_id = current.data(Qt.UserRole)
            return self.players.get(user_id)
        return None


class GameObjectsWidget(QWidget):
    """Виджет для отображения игровых объектов (локации, NPC, монстры)"""
    
    object_selected = pyqtSignal(dict)
    object_added = pyqtSignal(str, str, str)  # type, name, description
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.objects = {'locations': [], 'npcs': [], 'monsters': []}
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Вкладки для разных типов объектов
        from PyQt5.QtWidgets import QTabWidget
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                background-color: #3a3a3a;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: #e0e0e0;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background-color: #5a5a5a;
            }
        """)
        
        # Локации
        locations_tab = self.create_object_tab('locations', '📍 Локации')
        self.tabs.addTab(locations_tab, "📍 Локации")
        
        # NPC
        npcs_tab = self.create_object_tab('npcs', '👤 NPC')
        self.tabs.addTab(npcs_tab, "👤 NPC")
        
        # Монстры
        monsters_tab = self.create_object_tab('monsters', '👹 Монстры')
        self.tabs.addTab(monsters_tab, "👹 Монстры")
        
        layout.addWidget(self.tabs)
        
        # Кнопка добавления
        self.add_btn = QPushButton("➕ Добавить объект")
        self.add_btn.clicked.connect(self.add_object)
        layout.addWidget(self.add_btn)
        
        self.setLayout(layout)
    
    def create_object_tab(self, obj_type: str, title: str) -> QWidget:
        """Создает вкладку для объектов определенного типа"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        list_widget = QListWidget()
        list_widget.itemClicked.connect(lambda item, t=obj_type: self.on_object_clicked(t, item))
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: #3a3a3a;
                border: none;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
        """)
        layout.addWidget(list_widget)
        
        tab.setLayout(layout)
        
        # Сохраняем ссылку на список
        setattr(self, f"{obj_type}_list", list_widget)
        
        return tab
    
    def update_objects(self, obj_type: str, objects: list):
        """Обновляет список объектов определенного типа"""
        self.objects[obj_type] = objects
        
        list_widget = getattr(self, f"{obj_type}_list", None)
        if list_widget:
            list_widget.clear()
            
            icons = {'locations': '📍', 'npcs': '👤', 'monsters': '👹'}
            icon = icons.get(obj_type, '📦')
            
            for obj in objects:
                item = QListWidgetItem(f"{icon} {obj['name']}")
                item.setData(Qt.UserRole, obj)
                list_widget.addItem(item)
    
    def add_object(self, obj_type: str, name: str = None, description: str = None):
        """Добавляет новый объект"""
        if not name:
            name, ok = QInputDialog.getText(self, "Добавление объекта", "Название:")
            if not ok or not name:
                return
        
        if description is None:
            description, ok = QInputDialog.getText(self, "Добавление объекта", 
                                                   f"Описание для '{name}':",
                                                   QInputDialog.MultiLine)
            if not ok:
                description = ""
        
        self.object_added.emit(obj_type, name, description)
    
    def on_object_clicked(self, obj_type: str, item):
        """Обработчик выбора объекта"""
        obj = item.data(Qt.UserRole)
        self.object_selected.emit(obj)


class ActionButtonsWidget(QWidget):
    """Виджет с кнопками быстрых действий"""
    
    action_triggered = pyqtSignal(str, dict)  # action_name, params
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        layout = QGridLayout()
        layout.setSpacing(10)
        
        actions = [
            ("🎲 Бросок кубика", "roll_dice"),
            ("❤️ Лечение", "heal"),
            ("⚔️ Атака", "attack"),
            ("🛡️ Защита", "defend"),
            ("💊 Использовать предмет", "use_item"),
            ("🏃 Отдых", "rest"),
            ("📊 Проверить статы", "check_stats"),
            ("🎭 Действие", "action")
        ]
        
        for i, (label, action) in enumerate(actions):
            row = i // 2
            col = i % 2
            
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, a=action: self.action_triggered.emit(a, {}))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4a4a4a;
                    border: none;
                    border-radius: 6px;
                    padding: 10px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            layout.addWidget(btn, row, col)
        
        self.setLayout(layout)
    
    def set_enabled(self, enabled: bool):
        """Включает/выключает кнопки"""
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(enabled)