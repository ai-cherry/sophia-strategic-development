from flask import Blueprint, jsonify

company_bp = Blueprint('company', __name__)

@company_bp.route('/info')
def info():
    """Placeholder company info endpoint."""
        return jsonify({'message': 'Company info'}), 200
