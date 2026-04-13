# server/main.py
import sys
import io

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask_cors import CORS
from flask import Flask, jsonify
from server.config import Config
from server.models import db, User, Item

# Создаем приложение
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True, origins="*")

# Инициализация БД
db.init_app(app)

# Импортируем API Blueprints
from server.api.auth import auth_bp
from server.api.characters import characters_bp
from server.api.sessions import sessions_bp
from server.api.items import items_bp
from server.api.game_contexts import contexts_bp
from server.api.logs import logs_bp
from server.api.game import game_bp
from server.api.polling import polling_bp

# Регистрируем Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(characters_bp)
app.register_blueprint(sessions_bp)
app.register_blueprint(items_bp)
app.register_blueprint(contexts_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(game_bp)
app.register_blueprint(polling_bp)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


def init_db():
    """Инициализация базы данных и базовых предметов"""
    with app.app_context():
        db.create_all()
        
        # Добавляем базовые предметы
        if Item.query.count() == 0:
            starter_items = [
                Item(name='Рваная рубашка', description='Простая рубашка', 
                     item_type='armor', slot='body', icon='[Shirt]', is_equippable=True),
                Item(name='Деревянный меч', description='Тренировочный меч', 
                     item_type='weapon', slot='weapon', effects={'strength': 1}, icon='[Sword]', is_equippable=True),
                Item(name='Кожаные сапоги', description='Обычные сапоги', 
                     item_type='armor', slot='feet', effects={'dexterity': 1}, icon='[Boots]', is_equippable=True),
                Item(name='Целительное зелье', description='Восстанавливает 10 HP', 
                     item_type='consumable', is_equippable=False, effects={'heal_hp': 10}, icon='[Potion]'),
                Item(name='Магическое зелье', description='Восстанавливает 5 MP', 
                     item_type='consumable', is_equippable=False, effects={'heal_mp': 5}, icon='[Potion]'),
            ]
            
            for item in starter_items:
                db.session.add(item)
            
            db.session.commit()
            print("[DB] Starter items added")
        
        # Создаем админа если нет пользователей
        if User.query.count() == 0:
            admin = User(
                username="admin",
                email="admin@example.com",
                is_admin=True
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            print("[DB] Admin created: admin / admin123")
        
        print("[DB] Database initialized")


if __name__ == '__main__':
    init_db()
    print("=" * 50)
    print("DPJ Server started (HTTP Polling)")
    print("Address: http://localhost:5000")
    print("=" * 50)
    
    # Выводим все зарегистрированные маршруты для отладки
    print("\n[ROUTES] Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"   {methods:10} {rule.rule}")
    
    print("\n" + "=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)