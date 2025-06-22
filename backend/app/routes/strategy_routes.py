from flask import Blueprint, jsonify

strategy_bp = Blueprint('strategy', __name__)

@strategy_bp.route('/overview')
def overview():
    """Placeholder strategy overview endpoint."""
        return jsonify({'message': 'Strategy overview'}), 200
