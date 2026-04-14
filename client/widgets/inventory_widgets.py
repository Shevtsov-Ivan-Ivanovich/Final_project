# client/widgets/inventory_widgets.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem,
                             QDialog, QMessageBox, QSpinBox, QComboBox,
                             QTextEdit, QGroupBox, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal


class InventoryWidget(QWidget):
    """Виджет для отображения инвентаря персонажа"""
    
    item_used = pyqtSignal(dict)
    item_equipped = pyqtSignal(int, int)  # character_id, item_id
    item_unequipped = pyqtSignal(int, int)
    
    def __init__(self, api_client, character_id: int, is_editable: bool = False, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.character_id = character_id
        self.is_editable = is_editable
        self.inventory = []
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("📦 Инвентарь")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2ecc71;")
        layout.addWidget(title)
        
        # Экипировка
        equip_group = QGroupBox("⚔️ Экипировано")
        equip_layout = QVBoxLayout()
        self.equipped_list = QListWidget()
        self.equipped_list.itemDoubleClicked.connect(self.unequip_item)
        equip_layout.addWidget(self.equipped_list)
        equip_group.setLayout(equip_layout)
        layout.addWidget(equip_group)
        
        # Инвентарь
        inv_group = QGroupBox("📦 Инвентарь")
        inv_layout = QVBoxLayout()
        self.inventory_list = QListWidget()
        self.inventory_list.itemDoubleClicked.connect(self.use_item)
        inv_layout.addWidget(self.inventory_list)
        inv_group.setLayout(inv_layout)
        layout.addWidget(inv_group)
        
        # Кнопки (только для редактирования)
        if self.is_editable:
            btn_layout = QHBoxLayout()
            
            add_btn = QPushButton("➕ Добавить предмет")
            add_btn.clicked.connect(self.add_item)
            btn_layout.addWidget(add_btn)
            
            remove_btn = QPushButton("➖ Удалить предмет")
            remove_btn.clicked.connect(self.remove_item)
            btn_layout.addWidget(remove_btn)
            
            layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_inventory()
    
    def load_inventory(self):
        """Загружает инвентарь персонажа"""
        self.inventory = self.api_client.get_character_inventory(self.character_id)
        self.update_display()
    
    def update_display(self):
        """Обновляет отображение инвентаря"""
        self.equipped_list.clear()
        self.inventory_list.clear()
        
        for item in self.inventory:
            item_data = item.get('item_data', {})
            name = item.get('custom_name') or item_data.get('name', '?')
            icon = item_data.get('icon', '📦')
            qty = f" x{item['quantity']}" if item['quantity'] > 1 else ""
            description = item_data.get('description', '')
            
            display_text = f"{icon} {name}{qty}"
            if description:
                display_text += f"\n  {description[:50]}..."
            
            item_widget = QListWidgetItem(display_text)
            item_widget.setData(Qt.UserRole, item)
            
            if item.get('is_equipped'):
                self.equipped_list.addItem(item_widget)
            else:
                self.inventory_list.addItem(item_widget)
    
    def use_item(self, item):
        """Использует предмет"""
        current = self.inventory_list.currentItem()
        if not current:
            return
        
        item_data = current.data(Qt.UserRole)
        item_info = item_data.get('item_data', {})
        
        if item_info.get('is_equippable'):
            # Экипируем
            if self.api_client.equip_item(self.character_id, item_data['item_id']):
                self.load_inventory()
                self.item_equipped.emit(self.character_id, item_data['item_id'])
        elif item_info.get('item_type') == 'consumable':
            # Используем расходник
            self.item_used.emit(item_data)
            # Удаляем использованный предмет
            if self.api_client.remove_item_from_character(self.character_id, item_data['item_id']):
                self.load_inventory()
    
    def unequip_item(self, item):
        """Снимает предмет"""
        current = self.equipped_list.currentItem()
        if not current:
            return
        
        item_data = current.data(Qt.UserRole)
        if self.api_client.unequip_item(self.character_id, item_data['item_id']):
            self.load_inventory()
            self.item_unequipped.emit(self.character_id, item_data['item_id'])
    
    def add_item(self):
        """Добавляет предмет (для ГМ)"""
        dialog = ItemSelectorWidget(self.api_client, self.character_id, self)
        if dialog.exec_():
            self.load_inventory()
    
    def remove_item(self):
        """Удаляет предмет (для ГМ)"""
        current = self.inventory_list.currentItem()
        if not current:
            QMessageBox.warning(self, "Ошибка", "Выберите предмет для удаления")
            return
        
        item_data = current.data(Qt.UserRole)
        reply = QMessageBox.question(self, "Подтверждение", 
                                     f"Удалить предмет '{item_data.get('item_data', {}).get('name', '?')}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if self.api_client.remove_item_from_character(self.character_id, item_data['item_id']):
                self.load_inventory()
    
    def refresh(self):
        """Обновляет инвентарь"""
        self.load_inventory()


class ItemSelectorWidget(QDialog):
    """Диалог выбора предмета для выдачи"""
    
    def __init__(self, api_client, character_id: int, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.character_id = character_id
        self.items = []
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Выбор предмета")
        self.setMinimumSize(500, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #e0e0e0;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                color: #e0e0e0;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
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
            QSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                color: #e0e0e0;
                padding: 4px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Список предметов
        self.items_list = QListWidget()
        self.load_items()
        layout.addWidget(self.items_list)
        
        # Количество
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Количество:"))
        self.qty_spin = QSpinBox()
        self.qty_spin.setRange(1, 99)
        qty_layout.addWidget(self.qty_spin)
        qty_layout.addStretch()
        layout.addLayout(qty_layout)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.give_btn = QPushButton("✅ Выдать")
        self.give_btn.clicked.connect(self.give_item)
        self.give_btn.setEnabled(False)
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.give_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_items(self):
        """Загружает список доступных предметов"""
        self.items = self.api_client.get_all_items()
        self.items_list.clear()
        
        for item in self.items:
            effects_text = ""
            if item.get('effects'):
                effects = [f"{k}+{v}" for k, v in item['effects'].items() if v != 0]
                if effects:
                    effects_text = f" ({', '.join(effects)})"
            
            text = f"{item['icon']} {item['name']}{effects_text}\n  {item.get('description', '')[:60]}"
            item_widget = QListWidgetItem(text)
            item_widget.setData(Qt.UserRole, item['id'])
            self.items_list.addItem(item_widget)
        
        self.items_list.itemClicked.connect(self.on_item_selected)
    
    def on_item_selected(self, item):
        """Обработчик выбора предмета"""
        self.selected_item_id = item.data(Qt.UserRole)
        self.give_btn.setEnabled(True)
    
    def give_item(self):
        """Выдает предмет персонажу"""
        if hasattr(self, 'selected_item_id'):
            if self.api_client.add_item_to_character(self.character_id, self.selected_item_id, self.qty_spin.value()):
                QMessageBox.information(self, "Успех", "Предмет выдан!")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось выдать предмет")