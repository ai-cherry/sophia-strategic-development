from flask import Blueprint, jsonify

operations_bp = Blueprint('operations', __name__)

@operations_bp.route('/status')
def status():
    """Placeholder operations status endpoint."""
    return jsonify({'message': 'Operations status'}), 200
