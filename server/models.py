# server/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Таблица many-to-many для участников сессий
session_participants = db.Table(
    'session_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('session_id', db.Integer, db.ForeignKey('sessions.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    characters = db.relationship('Character', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }


class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    master_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Связи
    master = db.relationship('User', foreign_keys=[master_id])
    participants = db.relationship('User', secondary=session_participants, 
                                   backref=db.backref('sessions', lazy='dynamic'))
    characters = db.relationship('Character', backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'master_id': self.master_id,
            'master_name': self.master.username if self.master else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Character(db.Model):
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    experience = db.Column(db.Integer, default=0)
    
    # Характеристики
    strength = db.Column(db.Integer, default=10)
    dexterity = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    charisma = db.Column(db.Integer, default=10)
    
    # Текущие показатели
    current_hp = db.Column(db.Integer, default=10)
    current_mp = db.Column(db.Integer, default=5)
    max_hp = db.Column(db.Integer, default=10)
    max_mp = db.Column(db.Integer, default=5)
    
    # Внешние ключи
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'experience': self.experience,
            'stats': {
                'strength': self.strength,
                'dexterity': self.dexterity,
                'intelligence': self.intelligence,
                'charisma': self.charisma
            },
            'current_hp': self.current_hp,
            'current_mp': self.current_mp,
            'max_hp': self.max_hp,
            'max_mp': self.max_mp,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'session_name': self.session.name if self.session else None
        }


class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    item_type = db.Column(db.String(50), default='misc')  # weapon, armor, consumable, misc
    slot = db.Column(db.String(50), nullable=True)  # head, body, hands, feet, weapon, shield, finger, neck
    effects = db.Column(db.JSON, default={})  # {'strength': 2, 'dexterity': 1}
    icon = db.Column(db.String(10), default='📦')
    is_equippable = db.Column(db.Boolean, default=True)
    value = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'slot': self.slot,
            'effects': self.effects,
            'icon': self.icon,
            'is_equippable': self.is_equippable,
            'value': self.value
        }


class CharacterItem(db.Model):
    __tablename__ = 'character_items'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    is_equipped = db.Column(db.Boolean, default=False)
    custom_name = db.Column(db.String(100), nullable=True)
    custom_effects = db.Column(db.JSON, nullable=True)
    
    character = db.relationship('Character', backref='inventory_items')
    item = db.relationship('Item')
    
    def to_dict(self):
        return {
            'id': self.id,
            'character_id': self.character_id,
            'item_id': self.item_id,
            'item_data': self.item.to_dict() if self.item else None,
            'quantity': self.quantity,
            'is_equipped': self.is_equipped,
            'custom_name': self.custom_name,
            'custom_effects': self.custom_effects
        }


class GameLog(db.Model):
    __tablename__ = 'game_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)
    performer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=True)
    message = db.Column(db.Text, default="")
    details = db.Column(db.JSON, default={})
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    performer = db.relationship('User', foreign_keys=[performer_id])
    target = db.relationship('User', foreign_keys=[target_id])
    character = db.relationship('Character')
    session = db.relationship('Session')
    
    def to_dict(self):
        return {
            'id': self.id,
            'action_type': self.action_type,
            'performer_id': self.performer_id,
            'performer_name': self.performer.username if self.performer else None,
            'target_id': self.target_id,
            'target_name': self.target.username if self.target else None,
            'character_id': self.character_id,
            'character_name': self.character.name if self.character else None,
            'session_id': self.session_id,
            'session_name': self.session.name if self.session else None,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class GameContext(db.Model):
    __tablename__ = 'game_contexts'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    context_type = db.Column(db.String(50), nullable=False)  # location, npc, monster, object
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    data = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    session = db.relationship('Session', backref='game_contexts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'context_type': self.context_type,
            'name': self.name,
            'description': self.description,
            'data': self.data
        }