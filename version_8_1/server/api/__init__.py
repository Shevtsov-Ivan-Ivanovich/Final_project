# server/api/__init__.py
from server.api.auth import auth_bp
from server.api.characters import characters_bp
from server.api.sessions import sessions_bp
from server.api.items import items_bp
from server.api.game_contexts import contexts_bp
from server.api.logs import logs_bp
from server.api.game import game_bp
from server.api.polling import polling_bp 

__all__ = [
    'auth_bp',
    'characters_bp',
    'sessions_bp',
    'items_bp',
    'contexts_bp',
    'logs_bp',
    'game_bp',
    'polling_bp'
]