# client/styles.py
"""Файл со стилями для всего клиентского приложения"""

# Основные цвета
COLORS = {
    'bg_dark': '#2e2e2e',
    'bg_medium': '#3a3a3a',
    'bg_light': '#4a4a4a',
    'bg_lighter': '#5a5a5a',
    'text': '#e0e0e0',
    'text_muted': '#888888',
    'text_dark': '#bdc3c7',
    'accent': '#e67e22',
    'accent_hover': '#d35400',
    'success': '#2d6a4f',
    'success_hover': '#40916c',
    'danger': '#8b3a3a',
    'danger_hover': '#a04040',
    'warning': '#f39c12',
    'info': '#3498db',
    'hp': '#e74c3c',
    'mp': '#3498db',
    'chat_bg': '#2a2a2a'
}

# Основной стиль для главного окна
MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}
"""

# Стиль для виджетов
WIDGET_STYLE = f"""
    QWidget {{
        background-color: {COLORS['bg_dark']};
        font-family: 'Segoe UI', Arial, sans-serif;
        color: {COLORS['text']};
    }}
"""

# Стиль для кнопок
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['bg_light']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        color: white;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['bg_lighter']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['bg_medium']};
    }}
    QPushButton:disabled {{
        background-color: #555555;
        color: #888888;
    }}
"""

# Стиль для кнопки успеха (зеленой)
SUCCESS_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['success']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        color: white;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['success_hover']};
    }}
"""

# Стиль для кнопки опасности (красной)
DANGER_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['danger']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        color: white;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['danger_hover']};
    }}
"""

# Стиль для кнопки акцента (оранжевой)
ACCENT_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['accent']};
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        color: white;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['accent_hover']};
    }}
"""

# Стиль для полей ввода
INPUT_STYLE = f"""
    QLineEdit {{
        background-color: {COLORS['bg_medium']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 6px;
        padding: 8px;
        color: {COLORS['text']};
    }}
    QLineEdit:focus {{
        border-color: {COLORS['accent']};
    }}
    QLineEdit:disabled {{
        background-color: #555555;
        color: #888888;
    }}
"""

# Стиль для текстовых полей
TEXT_EDIT_STYLE = f"""
    QTextEdit {{
        background-color: {COLORS['bg_medium']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 6px;
        padding: 8px;
        color: {COLORS['text']};
        font-family: monospace;
    }}
    QTextEdit:focus {{
        border-color: {COLORS['accent']};
    }}
"""

# Стиль для списков
LIST_STYLE = f"""
    QListWidget {{
        background-color: {COLORS['bg_medium']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 6px;
        padding: 5px;
        color: {COLORS['text']};
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: 4px;
    }}
    QListWidget::item:hover {{
        background-color: {COLORS['bg_light']};
    }}
    QListWidget::item:selected {{
        background-color: {COLORS['accent']};
        color: white;
    }}
"""

# Стиль для комбобоксов
COMBO_STYLE = f"""
    QComboBox {{
        background-color: {COLORS['bg_medium']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 6px;
        padding: 6px;
        color: {COLORS['text']};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid {COLORS['text']};
        margin-right: 5px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        border: 1px solid {COLORS['bg_light']};
    }}
"""

# Стиль для групповых боксов
GROUP_BOX_STYLE = f"""
    QGroupBox {{
        color: {COLORS['text']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }}
"""

# Стиль для прогресс-баров
PROGRESS_BAR_STYLE = f"""
    QProgressBar {{
        border: 1px solid {COLORS['bg_light']};
        border-radius: 4px;
        text-align: center;
        color: white;
    }}
    QProgressBar::chunk {{
        border-radius: 3px;
    }}
"""

# Стиль для HP бара
HP_BAR_STYLE = f"""
    QProgressBar {{
        border: 1px solid {COLORS['bg_light']};
        border-radius: 4px;
        text-align: center;
        color: white;
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['hp']};
        border-radius: 3px;
    }}
"""

# Стиль для MP бара
MP_BAR_STYLE = f"""
    QProgressBar {{
        border: 1px solid {COLORS['bg_light']};
        border-radius: 4px;
        text-align: center;
        color: white;
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['mp']};
        border-radius: 3px;
    }}
"""

# Стиль для вкладок
TAB_STYLE = f"""
    QTabWidget::pane {{
        background-color: {COLORS['bg_medium']};
        border-radius: 8px;
    }}
    QTabBar::tab {{
        background-color: {COLORS['bg_light']};
        color: {COLORS['text']};
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background-color: {COLORS['accent']};
    }}
    QTabBar::tab:hover {{
        background-color: {COLORS['bg_lighter']};
    }}
"""

# Стиль для скроллбаров
SCROLLBAR_STYLE = f"""
    QScrollBar:vertical {{
        background-color: {COLORS['bg_medium']};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS['bg_light']};
        border-radius: 6px;
        min-height: 20px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['bg_lighter']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# Стиль для сплиттеров
SPLITTER_STYLE = f"""
    QSplitter::handle {{
        background-color: {COLORS['bg_light']};
    }}
    QSplitter::handle:hover {{
        background-color: {COLORS['accent']};
    }}
"""

# Стиль для чата
CHAT_STYLE = f"""
    QTextEdit {{
        background-color: {COLORS['chat_bg']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 8px;
        padding: 10px;
        color: {COLORS['text']};
        font-family: 'Segoe UI', monospace;
        font-size: 12px;
    }}
"""

# Стиль для диалогов
DIALOG_STYLE = f"""
    QDialog {{
        background-color: {COLORS['bg_dark']};
    }}
    QDialog QLabel {{
        color: {COLORS['text']};
    }}
"""

# Стиль для статусной строки
STATUS_BAR_STYLE = f"""
    QStatusBar {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text']};
    }}
"""

# Стиль для меню
MENU_STYLE = f"""
    QMenuBar {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text']};
    }}
    QMenuBar::item:selected {{
        background-color: {COLORS['accent']};
    }}
    QMenu {{
        background-color: {COLORS['bg_medium']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['bg_light']};
    }}
    QMenu::item:selected {{
        background-color: {COLORS['accent']};
    }}
"""

# Стиль для спинбоксов
SPINBOX_STYLE = f"""
    QSpinBox {{
        background-color: {COLORS['bg_medium']};
        border: 1px solid {COLORS['bg_light']};
        border-radius: 6px;
        padding: 4px;
        color: {COLORS['text']};
    }}
    QSpinBox:focus {{
        border-color: {COLORS['accent']};
    }}
"""

# Полный стиль приложения (собирает все вышеперечисленное)
FULL_STYLE = f"""
    {WIDGET_STYLE}
    {BUTTON_STYLE}
    {INPUT_STYLE}
    {TEXT_EDIT_STYLE}
    {LIST_STYLE}
    {COMBO_STYLE}
    {GROUP_BOX_STYLE}
    {TAB_STYLE}
    {SCROLLBAR_STYLE}
    {SPLITTER_STYLE}
    {CHAT_STYLE}
    {DIALOG_STYLE}
    {STATUS_BAR_STYLE}
    {MENU_STYLE}
    {SPINBOX_STYLE}
    
    /* Дополнительные стили */
    QFrame {{
        border-radius: 8px;
    }}
    
    QLabel {{
        color: {COLORS['text']};
    }}
    
    QLabel#title {{
        font-size: 24px;
        font-weight: bold;
        color: {COLORS['accent']};
    }}
    
    QLabel#subtitle {{
        font-size: 14px;
        color: {COLORS['text_muted']};
    }}
    
    QLabel#error {{
        color: {COLORS['danger']};
    }}
    
    QLabel#success {{
        color: {COLORS['success']};
    }}
"""

def get_button_style(button_type: str = "default") -> str:
    """Возвращает стиль кнопки в зависимости от типа"""
    styles = {
        "default": BUTTON_STYLE,
        "success": SUCCESS_BUTTON_STYLE,
        "danger": DANGER_BUTTON_STYLE,
        "accent": ACCENT_BUTTON_STYLE
    }
    return styles.get(button_type, BUTTON_STYLE)

def get_progress_bar_style(bar_type: str = "default") -> str:
    """Возвращает стиль прогресс-бара в зависимости от типа"""
    styles = {
        "default": PROGRESS_BAR_STYLE,
        "hp": HP_BAR_STYLE,
        "mp": MP_BAR_STYLE
    }
    return styles.get(bar_type, PROGRESS_BAR_STYLE)