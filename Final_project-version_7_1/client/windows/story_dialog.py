# client/windows/story_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QTabWidget, QWidget,
                             QListWidget, QMessageBox, QFileDialog, QSplitter,
                             QApplication, QInputDialog, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt
import re
import json
import os
from datetime import datetime


class StoryDialog(QDialog):
    """Диалог для работы с сюжетом"""
    
    def __init__(self, api_client, user_data, session_id=None, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.user_data = user_data
        self.session_id = session_id
        self.extracted_items = {
            'locations': [],
            'characters': [],
            'monsters': [],
            'items': []
        }
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Редактор сюжета")
        self.setMinimumSize(1000, 750)
        self.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title = QLabel("Создание и редактирование сюжета")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #e67e22; margin: 10px;")
        layout.addWidget(title)
        
        tabs = QTabWidget()
        
        # Вкладка редактирования
        edit_tab = self.create_edit_tab()
        tabs.addTab(edit_tab, "✏️ Редактор")
        
        # Вкладка элементов
        elements_tab = self.create_elements_tab()
        tabs.addTab(elements_tab, "📋 Выделенные элементы")
        
        layout.addWidget(tabs)
        
        # Кнопки диалога
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def get_stylesheet(self):
        return """
            QDialog {
                background-color: #2e2e2e;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Courier New', monospace;
                color: #e0e0e0;
            }
            QListWidget {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
                border-radius: 8px;
                padding: 8px;
                color: #e0e0e0;
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
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton#save_btn {
                background-color: #2d6a4f;
            }
            QPushButton#save_btn:hover {
                background-color: #40916c;
            }
            QPushButton#extract_btn {
                background-color: #e67e22;
            }
            QPushButton#extract_btn:hover {
                background-color: #d35400;
            }
            QPushButton#clear_btn {
                background-color: #8b3a3a;
            }
            QPushButton#clear_btn:hover {
                background-color: #a04040;
            }
            QPushButton#import_btn {
                background-color: #9b59b6;
            }
            QPushButton#import_btn:hover {
                background-color: #8e44ad;
            }
            QTabWidget::pane {
                background-color: #3a3a3a;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: #e0e0e0;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #5a5a5a;
            }
            QSplitter::handle {
                background-color: #4a4a4a;
            }
        """
    
    def create_edit_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.story_text = QTextEdit()
        self.story_text.setPlaceholderText("""
Введите текст сюжета здесь...

Пример:
"В старом замке, на вершине горы, жил могущественный дракон. 
Рыцарь Артур отправился в опасное путешествие, чтобы победить чудовище 
и найти древний артефакт - Меч Судьбы."

Система автоматически выделит:
- Локации (замок, гора)
- Персонажей (рыцарь Артур)
- Монстров (дракон)
- Предметы (Меч Судьбы)
        """.strip())
        layout.addWidget(self.story_text)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        import_btn = QPushButton("📁 Импорт из TXT")
        import_btn.setObjectName("import_btn")
        import_btn.clicked.connect(self.import_story)
        btn_layout.addWidget(import_btn)
        
        add_element_btn = QPushButton("✨ Добавить элемент")
        add_element_btn.setObjectName("add_element_btn")
        add_element_btn.setStyleSheet("background-color: #9b59b6;")
        add_element_btn.clicked.connect(self.add_custom_element)
        btn_layout.addWidget(add_element_btn)
        
        extract_btn = QPushButton("🔍 Выделить элементы")
        extract_btn.setObjectName("extract_btn")
        extract_btn.clicked.connect(self.extract_elements)
        btn_layout.addWidget(extract_btn)
        
        clear_btn = QPushButton("🗑 Очистить")
        clear_btn.setObjectName("clear_btn")
        clear_btn.clicked.connect(self.clear_text)
        btn_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("💾 Сохранить сюжет")
        save_btn.setObjectName("save_btn")
        save_btn.clicked.connect(self.save_story)
        btn_layout.addWidget(save_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_elements_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Статистика
        stats_frame = QWidget()
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Статистика: ожидание...")
        self.stats_label.setStyleSheet("color: #f39c12; font-size: 12px;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Сплиттер для списков
        splitter = QSplitter(Qt.Horizontal)
        
        # Локации
        locations_widget = QWidget()
        locations_layout = QVBoxLayout()
        locations_label = QLabel("📍 ЛОКАЦИИ")
        locations_label.setStyleSheet("color: #3498db; font-size: 14px;")
        locations_layout.addWidget(locations_label)
        self.locations_list = QListWidget()
        self.locations_list.itemClicked.connect(lambda item: self.show_context(item, 'location'))
        locations_layout.addWidget(self.locations_list)
        locations_widget.setLayout(locations_layout)
        
        # Персонажи
        characters_widget = QWidget()
        characters_layout = QVBoxLayout()
        characters_label = QLabel("👤 ПЕРСОНАЖИ")
        characters_label.setStyleSheet("color: #2ecc71; font-size: 14px;")
        characters_layout.addWidget(characters_label)
        self.characters_list = QListWidget()
        self.characters_list.itemClicked.connect(lambda item: self.show_context(item, 'character'))
        characters_layout.addWidget(self.characters_list)
        characters_widget.setLayout(characters_layout)
        
        # Монстры
        monsters_widget = QWidget()
        monsters_layout = QVBoxLayout()
        monsters_label = QLabel("👹 МОНСТРЫ")
        monsters_label.setStyleSheet("color: #e74c3c; font-size: 14px;")
        monsters_layout.addWidget(monsters_label)
        self.monsters_list = QListWidget()
        self.monsters_list.itemClicked.connect(lambda item: self.show_context(item, 'monster'))
        monsters_layout.addWidget(self.monsters_list)
        monsters_widget.setLayout(monsters_layout)
        
        # Предметы
        items_widget = QWidget()
        items_layout = QVBoxLayout()
        items_label = QLabel("📦 ПРЕДМЕТЫ")
        items_label.setStyleSheet("color: #f1c40f; font-size: 14px;")
        items_layout.addWidget(items_label)
        self.items_list = QListWidget()
        self.items_list.itemClicked.connect(lambda item: self.show_context(item, 'item'))
        items_layout.addWidget(self.items_list)
        items_widget.setLayout(items_layout)
        
        splitter.addWidget(locations_widget)
        splitter.addWidget(characters_widget)
        splitter.addWidget(monsters_widget)
        splitter.addWidget(items_widget)
        layout.addWidget(splitter)
        
        # Контекст
        context_label = QLabel("Контекст:")
        context_label.setStyleSheet("margin-top: 10px;")
        layout.addWidget(context_label)
        
        self.context_text = QTextEdit()
        self.context_text.setReadOnly(True)
        self.context_text.setMaximumHeight(100)
        self.context_text.setStyleSheet("background-color: #2a2a2a; color: #e0e0e0;")
        layout.addWidget(self.context_text)
        
        tab.setLayout(layout)
        return tab
    
    def add_custom_element(self):
        """Добавляет пользовательский элемент в сюжет"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавление элемента")
        dialog.setMinimumSize(400, 350)
        dialog.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Тип элемента
        layout.addWidget(QLabel("Тип элемента:"))
        type_combo = QComboBox()
        type_combo.addItems(["Локация", "Персонаж", "Монстр", "Предмет", "Событие"])
        layout.addWidget(type_combo)
        
        # Название
        layout.addWidget(QLabel("Название:"))
        name_input = QLineEdit()
        name_input.setPlaceholderText("Введите название...")
        layout.addWidget(name_input)
        
        # Описание
        layout.addWidget(QLabel("Описание/контекст:"))
        desc_input = QTextEdit()
        desc_input.setPlaceholderText("Введите описание...")
        desc_input.setMaximumHeight(100)
        layout.addWidget(desc_input)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("✅ Добавить")
        add_btn.setStyleSheet("background-color: #2d6a4f;")
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet("background-color: #8b3a3a;")
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        def on_add():
            element_type = type_combo.currentText().lower()
            name = name_input.text().strip()
            description = desc_input.toPlainText().strip()
            
            if not name:
                QMessageBox.warning(dialog, "Ошибка", "Введите название элемента")
                return
            
            # Добавляем элемент в текст сюжета
            current_text = self.story_text.toPlainText()
            new_element = f"\n\n[{element_type.upper()}] {name}"
            if description:
                new_element += f"\nОписание: {description}"
            
            self.story_text.setPlainText(current_text + new_element)
            
            # Логируем
            self.api_client.create_log(
                f'story_{element_type}',
                self.user_data['id'],
                session_id=self.session_id,
                details={'name': name, 'context': description}
            )
            
            QMessageBox.information(dialog, "Успех", f"Элемент '{name}' добавлен в сюжет!")
            dialog.accept()
            
            # Предлагаем выделить элементы
            reply = QMessageBox.question(self, "Выделение элементов",
                                        "Выделить все элементы в сюжете?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.extract_elements()
        
        add_btn.clicked.connect(on_add)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def import_story(self):
        """Импортирует сюжет из TXT файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл с сюжетом", 
            "", 
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Пробуем разные кодировки
            encodings = ['utf-8', 'cp1251', 'cp866', 'latin-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                QMessageBox.warning(self, "Ошибка", "Не удалось прочитать файл. Проверьте кодировку.")
                return
            
            # Спрашиваем, заменить текущий текст или добавить
            current_text = self.story_text.toPlainText()
            
            if current_text.strip():
                reply = QMessageBox.question(
                    self, 
                    "Импорт сюжета",
                    "Заменить текущий текст или добавить в конец?\n\n"
                    "Да - заменить\n"
                    "Нет - добавить в конец\n"
                    "Отмена - отменить импорт",
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Cancel:
                    return
                elif reply == QMessageBox.Yes:
                    self.story_text.setPlainText(content)
                else:
                    self.story_text.setPlainText(current_text + "\n\n" + content)
            else:
                self.story_text.setPlainText(content)
            
            # Автоматически выделяем элементы после импорта
            reply = QMessageBox.question(
                self,
                "Выделение элементов",
                "Выделить элементы из импортированного сюжета?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.extract_elements()
            
            # Логируем импорт
            self.api_client.create_log(
                'import_story',
                self.user_data['id'],
                session_id=self.session_id,
                details={'filename': os.path.basename(file_path)}
            )
            
            QMessageBox.information(self, "Успех", f"Сюжет импортирован из:\n{file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при импорте файла:\n{str(e)}")
    
    def extract_elements(self):
        """Выделяет элементы из текста"""
        text = self.story_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Предупреждение", "Введите текст сюжета")
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        try:
            elements = self.parse_story_text(text)
            self.extracted_items = elements
            
            # Обновляем списки
            self.locations_list.clear()
            for loc in elements['locations']:
                self.locations_list.addItem(f"{loc['name']}")
                self.locations_list.item(self.locations_list.count() - 1).setData(Qt.UserRole, loc)
            
            self.characters_list.clear()
            for char in elements['characters']:
                self.characters_list.addItem(f"{char['name']}")
                self.characters_list.item(self.characters_list.count() - 1).setData(Qt.UserRole, char)
            
            self.monsters_list.clear()
            for monster in elements['monsters']:
                self.monsters_list.addItem(f"{monster['name']}")
                self.monsters_list.item(self.monsters_list.count() - 1).setData(Qt.UserRole, monster)
            
            self.items_list.clear()
            for item in elements['items']:
                self.items_list.addItem(f"{item['name']}")
                self.items_list.item(self.items_list.count() - 1).setData(Qt.UserRole, item)
            
            # Обновляем статистику
            total = (len(elements['locations']) + len(elements['characters']) + 
                    len(elements['monsters']) + len(elements['items']))
            self.stats_label.setText(
                f"📊 Статистика: Локации: {len(elements['locations'])} | "
                f"Персонажи: {len(elements['characters'])} | "
                f"Монстры: {len(elements['monsters'])} | "
                f"Предметы: {len(elements['items'])} | "
                f"Всего: {total}"
            )
            
            # Логируем выделенные элементы
            for loc in elements['locations']:
                self.api_client.create_log(
                    'story_location',
                    self.user_data['id'],
                    session_id=self.session_id,
                    details={'location': loc['name'], 'context': loc['context']}
                )
            
            for char in elements['characters']:
                self.api_client.create_log(
                    'story_character',
                    self.user_data['id'],
                    session_id=self.session_id,
                    details={'character': char['name'], 'context': char['context']}
                )
            
            for monster in elements['monsters']:
                self.api_client.create_log(
                    'story_monster',
                    self.user_data['id'],
                    session_id=self.session_id,
                    details={'monster': monster['name'], 'context': monster['context']}
                )
            
            for item in elements['items']:
                self.api_client.create_log(
                    'story_item',
                    self.user_data['id'],
                    session_id=self.session_id,
                    details={'item': item['name'], 'context': item['context']}
                )
            
            QMessageBox.information(
                self, "Готово",
                f"Выделено элементов:\n\n"
                f"📍 Локации: {len(elements['locations'])}\n"
                f"👤 Персонажи: {len(elements['characters'])}\n"
                f"👹 Монстры: {len(elements['monsters'])}\n"
                f"📦 Предметы: {len(elements['items'])}\n"
                f"\nВсе элементы сохранены в лог!"
            )
            
        finally:
            QApplication.restoreOverrideCursor()
    
    def parse_story_text(self, text: str):
        """Парсит текст и выделяет ключевые элементы"""
        
        location_keywords = ['город', 'деревня', 'замок', 'пещера', 'лес', 'гора', 'долина', 
                            'таверна', 'храм', 'башня', 'подземелье', 'дворец', 'площадь',
                            'крепость', 'руины', 'болото', 'пустыня', 'озеро', 'река', 'море']
        
        character_keywords = ['король', 'королева', 'принц', 'принцесса', 'лорд', 'леди', 
                             'рыцарь', 'маг', 'волшебник', 'жрец', 'купец', 'крестьянин',
                             'воин', 'разбойник', 'бард', 'друид', 'паладин', 'монах']
        
        monster_keywords = ['дракон', 'гоблин', 'орк', 'тролль', 'скелет', 'зомби', 'вампир',
                           'оборотень', 'гигант', 'демон', 'призрак', 'гарпия', 'минотавр',
                           'паук', 'волк', 'медведь', 'элементаль', 'голем']
        
        item_keywords = ['меч', 'щит', 'кольцо', 'амулет', 'зелье', 'свиток', 'артефакт',
                        'книга', 'ключ', 'сундук', 'сокровище', 'золото', 'оружие', 'броня',
                        'шлем', 'перчатки', 'сапоги', 'плащ', 'посох', 'лук', 'стрелы']
        
        extracted = {
            'locations': [],
            'characters': [],
            'monsters': [],
            'items': []
        }
        
        # Разбиваем на предложения
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Поиск локаций
            for kw in location_keywords:
                if kw in sentence_lower:
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if kw in word.lower():
                            location_name = ' '.join(words[max(0, i-2):min(len(words), i+3)])
                            extracted['locations'].append({
                                'name': location_name.strip(),
                                'context': sentence.strip(),
                                'keyword': kw
                            })
                            break
            
            # Поиск персонажей
            for kw in character_keywords:
                if kw in sentence_lower:
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if kw in word.lower():
                            # Ищем имя персонажа (обычно перед ключевым словом)
                            start = max(0, i-3)
                            char_name = ' '.join(words[start:min(len(words), i+2)])
                            extracted['characters'].append({
                                'name': char_name.strip(),
                                'context': sentence.strip(),
                                'keyword': kw
                            })
                            break
            
            # Поиск монстров
            for kw in monster_keywords:
                if kw in sentence_lower:
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if kw in word.lower():
                            monster_name = ' '.join(words[max(0, i-2):min(len(words), i+3)])
                            extracted['monsters'].append({
                                'name': monster_name.strip(),
                                'context': sentence.strip(),
                                'keyword': kw
                            })
                            break
            
            # Поиск предметов
            for kw in item_keywords:
                if kw in sentence_lower:
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if kw in word.lower():
                            item_name = ' '.join(words[max(0, i-2):min(len(words), i+3)])
                            extracted['items'].append({
                                'name': item_name.strip(),
                                'context': sentence.strip(),
                                'keyword': kw
                            })
                            break
        
        # Удаляем дубликаты
        for key in extracted:
            extracted[key] = self.remove_duplicates(extracted[key])
        
        return extracted
    
    def remove_duplicates(self, items):
        """Удаляет дубликаты из списка"""
        seen = set()
        unique = []
        for item in items:
            name_key = item['name'].lower()
            if name_key not in seen:
                seen.add(name_key)
                unique.append(item)
        return unique
    
    def show_context(self, item, element_type):
        """Показывает контекст выбранного элемента"""
        element = item.data(Qt.UserRole)
        if element:
            context = element.get('context', 'Нет контекста')
            keyword = element.get('keyword', '?')
            self.context_text.setText(f"📌 Элемент: {element['name']}\n"
                                      f"🔑 Ключевое слово: {keyword}\n"
                                      f"📝 Контекст: {context}")
    
    def clear_text(self):
        """Очищает весь текст и списки"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить весь текст и выделенные элементы?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.story_text.clear()
            self.locations_list.clear()
            self.characters_list.clear()
            self.monsters_list.clear()
            self.items_list.clear()
            self.context_text.clear()
            self.stats_label.setText("Статистика: ожидание...")
            self.extracted_items = {'locations': [], 'characters': [], 'monsters': [], 'items': []}
            
            self.api_client.create_log(
                'clear_story',
                self.user_data['id'],
                session_id=self.session_id
            )
    
    def save_story(self):
        """Сохраняет сюжет в файл"""
        text = self.story_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Предупреждение", "Нет текста для сохранения")
            return
        
        if not self.locations_list.count():
            reply = QMessageBox.question(
                self, "Выделение элементов",
                "Выделить элементы перед сохранением?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.extract_elements()
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить сюжет", "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        
        if filename:
            saved_file = self.save_story_to_file(text, filename)
            QMessageBox.information(self, "Успех", f"Сюжет сохранен в:\n{saved_file}")
            
            self.api_client.create_log(
                'save_story',
                self.user_data['id'],
                session_id=self.session_id,
                details={'filename': filename}
            )
    
    def save_story_to_file(self, text: str, filename: str = None) -> str:
        """Сохраняет текст сюжета в файл"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"story_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"=== СЮЖЕТ ===\n")
            f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            f.write(text)
            f.write(f"\n\n{'='*50}\n")
            f.write(f"=== ВЫДЕЛЕННЫЕ ЭЛЕМЕНТЫ ===\n\n")
            
            f.write("📍 ЛОКАЦИИ:\n")
            for loc in self.extracted_items['locations']:
                f.write(f"  - {loc['name']}\n")
                f.write(f"    Контекст: {loc['context'][:100]}...\n")
            
            f.write("\n👤 ПЕРСОНАЖИ:\n")
            for char in self.extracted_items['characters']:
                f.write(f"  - {char['name']}\n")
            
            f.write("\n👹 МОНСТРЫ/ПРОТИВНИКИ:\n")
            for monster in self.extracted_items['monsters']:
                f.write(f"  - {monster['name']}\n")
            
            f.write("\n📦 ПРЕДМЕТЫ:\n")
            for item in self.extracted_items['items']:
                f.write(f"  - {item['name']}\n")
        
        return filename