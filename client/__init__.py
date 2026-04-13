# client/__init__.py
from client.api_client import APIClient, api_client
from client.socket_client import SocketClient  # Только класс, не экземпляр
from client.config_manager import config_manager
from client.styles import FULL_STYLE, COLORS
from client.windows.login_window import LoginWindow
from client.windows.role_window import RoleWindow
from client.windows.gm_window import GMWindow
from client.windows.player_window import PlayerWindow
from client.windows.story_dialog import StoryDialog

__all__ = [
    'APIClient',
    'api_client',
    'SocketClient',
    'config_manager', 
    'FULL_STYLE',
    'COLORS',
    'LoginWindow',
    'RoleWindow',
    'GMWindow',
    'PlayerWindow',
    'StoryDialog'
]