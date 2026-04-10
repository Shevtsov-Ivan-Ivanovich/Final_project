# server/api/logs.py
from flask import Blueprint, request, jsonify, g
from server.models import db, User, GameLog, Character, Session

logs_bp = Blueprint('logs', __name__, url_prefix='/api/logs')


class LogService:
    @staticmethod
    def log_action(action_type, performer_id, target_id=None, character_id=None, 
                   session_id=None, message=None, details=None):
        log = GameLog(
            action_type=action_type,
            performer_id=performer_id,
            target_id=target_id,
            character_id=character_id,
            session_id=session_id,
            message=message or '',
            details=details or {}
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def get_logs_for_gm(limit=100, session_id=None, character_id=None):
        query = GameLog.query
        if session_id:
            query = query.filter_by(session_id=session_id)
        if character_id:
            query = query.filter_by(character_id=character_id)
        return query.order_by(GameLog.timestamp.desc()).limit(limit).all()
    
    @staticmethod
    def get_logs_for_player(player_id, limit=100):
        return GameLog.query.filter(
            (GameLog.performer_id == player_id) | (GameLog.target_id == player_id)
        ).order_by(GameLog.timestamp.desc()).limit(limit).all()


@logs_bp.route('/', methods=['POST'])
def create_log():
    data = request.json
    log = LogService.log_action(
        action_type=data['action_type'],
        performer_id=data['performer_id'],
        target_id=data.get('target_id'),
        character_id=data.get('character_id'),
        session_id=data.get('session_id'),
        message=data.get('message'),
        details=data.get('details')
    )
    return jsonify({'success': True, 'log': log.to_dict()}), 201


@logs_bp.route('/gm', methods=['GET'])
def get_gm_logs():
    session_id = request.args.get('session_id', type=int)
    character_id = request.args.get('character_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    
    logs = LogService.get_logs_for_gm(limit, session_id, character_id)
    return jsonify([l.to_dict() for l in logs]), 200


@logs_bp.route('/player/<int:player_id>', methods=['GET'])
def get_player_logs(player_id):
    limit = request.args.get('limit', 100, type=int)
    logs = LogService.get_logs_for_player(player_id, limit)
    return jsonify([l.to_dict() for l in logs]), 200


@logs_bp.route('/session/<int:session_id>', methods=['GET'])
def get_session_logs(session_id):
    logs = GameLog.query.filter_by(session_id=session_id)\
        .order_by(GameLog.timestamp.desc()).limit(200).all()
    return jsonify([l.to_dict() for l in logs]), 200