# client/widgets/__init__.py
from client.widgets.character_widgets import CharacterStatsWidget, CharacterSelectorWidget
from client.widgets.inventory_widgets import InventoryWidget, ItemSelectorWidget
from client.widgets.chat_widget import ChatWidget

__all__ = [
    'CharacterStatsWidget',
    'CharacterSelectorWidget',
    'InventoryWidget',
    'ItemSelectorWidget',
    'ChatWidget'
]