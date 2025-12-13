from flask import Blueprint, jsonify
from extensions import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with service status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Innsight AI API'
    }), 200

@health_bp.route('/health/db', methods=['GET'])
def database_health():
    """
    Database health check endpoint.
    
    Returns:
        JSON response with database connection status
    """
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }), 503