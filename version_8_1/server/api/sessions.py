# server/api/sessions.py
from flask import Blueprint, request, jsonify
from server.models import db, User, Session, Character

sessions_bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')


@sessions_bp.route('/', methods=['GET'])
def get_sessions():
    sessions = Session.query.all()
    return jsonify([s.to_dict() for s in sessions]), 200


@sessions_bp.route('/my/<int:user_id>', methods=['GET'])
def get_my_sessions(user_id):
    user = User.query.get_or_404(user_id)
    sessions = user.sessions.all()
    return jsonify([s.to_dict() for s in sessions]), 200


@sessions_bp.route('/available/<int:user_id>', methods=['GET'])
def get_available_sessions(user_id):
    user = User.query.get_or_404(user_id)
    my_session_ids = [s.id for s in user.sessions.all()]
    sessions = Session.query.filter(~Session.id.in_(my_session_ids)).all()
    return jsonify([s.to_dict() for s in sessions]), 200


@sessions_bp.route('/', methods=['POST'])
def create_session():
    data = request.json
    
    session = Session(
        name=data['name'],
        description=data.get('description', ''),
        master_id=data['master_id']
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'success': True, 'session': session.to_dict()}), 201


@sessions_bp.route('/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    session = Session.query.get_or_404(session_id)
    
    # Открепляем персонажей
    Character.query.filter_by(session_id=session_id).update({'session_id': None})
    
    db.session.delete(session)
    db.session.commit()
    
    return jsonify({'success': True}), 200


@sessions_bp.route('/<int:session_id>/join', methods=['POST'])
def join_session(session_id):
    data = request.json
    user_id = data.get('user_id')
    
    session = Session.query.get_or_404(session_id)
    user = User.query.get_or_404(user_id)
    
    if user not in session.participants:
        session.participants.append(user)
        db.session.commit()
    
    return jsonify({'success': True}), 200


@sessions_bp.route('/<int:session_id>/leave', methods=['POST'])
def leave_session(session_id):
    data = request.json
    user_id = data.get('user_id')
    
    session = Session.query.get_or_404(session_id)
    user = User.query.get_or_404(user_id)
    
    if user in session.participants:
        session.participants.remove(user)
        db.session.commit()
    
    return jsonify({'success': True}), 200


@sessions_bp.route('/<int:session_id>/participants', methods=['GET'])
def get_participants(session_id):
    session = Session.query.get_or_404(session_id)
    participants = []
    
    for user in session.participants.all():
        character = Character.query.filter_by(user_id=user.id, session_id=session_id).first()
        participants.append({
            'user_id': user.id,
            'username': user.username,
            'character_id': character.id if character else None,
            'character_name': character.name if character else None
        })
    
    return jsonify({'participants': participants}), 200