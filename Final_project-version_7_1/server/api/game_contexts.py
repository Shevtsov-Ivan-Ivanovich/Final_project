# server/api/game_contexts.py
from flask import Blueprint, request, jsonify
from server.models import db, GameContext

contexts_bp = Blueprint('game_contexts', __name__, url_prefix='/api/game_contexts')


@contexts_bp.route('/session/<int:session_id>', methods=['GET'])
def get_session_contexts(session_id):
    contexts = GameContext.query.filter_by(session_id=session_id).all()
    return jsonify([c.to_dict() for c in contexts]), 200


@contexts_bp.route('/', methods=['POST'])
def create_context():
    data = request.json
    
    context = GameContext(
        session_id=data['session_id'],
        context_type=data['context_type'],
        name=data['name'],
        description=data.get('description', ''),
        data=data.get('data', {})
    )
    
    db.session.add(context)
    db.session.commit()
    
    return jsonify({'success': True, 'context': context.to_dict()}), 201


@contexts_bp.route('/<int:context_id>', methods=['DELETE'])
def delete_context(context_id):
    context = GameContext.query.get_or_404(context_id)
    db.session.delete(context)
    db.session.commit()
    
    return jsonify({'success': True}), 200