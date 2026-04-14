# server/api/auth.py
from flask import Blueprint, request, jsonify
from server.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Все поля обязательны'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Логин уже занят'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email уже зарегистрирован'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    login_or_email = data.get('login_or_email')
    password = data.get('password')
    
    if not login_or_email or not password:
        return jsonify({'error': 'Все поля обязательны'}), 400
    
    user = User.query.filter(
        (User.username == login_or_email) | (User.email == login_or_email)
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Неверный логин/email или пароль'}), 401
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200