import logging
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy import inspect

from config import get_config
from extensions import init_extensions, db
from routes.health_bp import health_bp
from routes.hotels_bp import hotels_bp
from routes.reviews_bp import reviews_bp
from models.hotel import Hotel


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration name (development/testing/production)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    config = get_config(config_name)
    app.config.from_object(config)
    
    setup_logging(app)
    init_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)
    
    app.logger.info(f"Application started in {app.config.get('FLASK_ENV', 'development')} mode")
    
    return app


def setup_logging(app):
    """
    Configure application logging.
    
    Args:
        app: Flask application
    """
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Set Flask app logger level
    app.logger.setLevel(log_level)
    
    # Reduce noise from external libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('pika').setLevel(logging.WARNING)


def register_blueprints(app):
    """
    Register all Flask blueprints.
    
    Args:
        app: Flask application
    """
    app.register_blueprint(health_bp)
    
    # API routes (with version prefix)
    api_prefix = app.config['API_PREFIX']
    app.register_blueprint(hotels_bp, url_prefix=f'{api_prefix}/hotels')
    app.register_blueprint(reviews_bp, url_prefix=f'{api_prefix}/reviews')
    
    app.logger.info(f"Registered blueprints with prefix: {api_prefix}")


def register_error_handlers(app):
    """
    Register global error handlers.
    
    Args:
        app: Flask application
    """
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions"""
        return jsonify({
            'error': e.name,
            'message': e.description
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_general_exception(e):
        """Handle unexpected exceptions"""
        app.logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """Handle 405 errors"""
        return jsonify({
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL'
        }), 405

def ensure_database_setup(app):
    """
    Ensure database is properly initialized.
    
    Creates tables if they don't exist and seeds initial data if database is empty.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        app.logger.info(f"📊 Existing database tables: {existing_tables}")
        
        if 'hotels' not in existing_tables:
            _create_tables(app, inspector)
        else:
            _check_and_seed_data(app)

def _create_tables(app, inspector):
    """
    Create database tables.
    
    Args:
        app: Flask application instance
        inspector: SQLAlchemy inspector instance
    """
    app.logger.info("Tables not found. Creating database schema...")

    try:
        db.create_all()
        
        new_inspector = inspect(db.engine)
        new_tables = new_inspector.get_table_names()
        app.logger.info(f"Successfully created tables: {new_tables}")
        
        if 'hotels' not in new_tables:
            raise Exception("Failed to create 'hotels' table")
        
        # Seed initial data
        _seed_sample_data(app)
        
    except Exception as error:
        app.logger.error(f"Error creating tables: {error}")
        raise

def _check_and_seed_data(app):
    """
    Check if database has data and seed if empty.
    
    Args:
        app: Flask application instance
    """
    try:
        hotel_count = db.session.query(Hotel).count()
        app.logger.info(f"Found {hotel_count} hotels in database")
        
        if hotel_count == 0:
            app.logger.info("Database is empty. Seeding initial data...")
            _seed_sample_data(app)
        else:
            app.logger.info("Database already contains data. Skipping seed.")
            
    except Exception as error:
        app.logger.error(f"Error checking database data: {error}")
        raise

def _seed_sample_data(app):
    """Seed database with sample hotels"""
    from sqlalchemy import text
    
    try:
        db.session.rollback()
        
        hotels = [
            Hotel(
                name="Grand Plaza Hotel",
                city="New York",
                country="USA",
                address="123 Main St, NY 10001",
                description="Luxury hotel in the heart of Manhattan",
                star_rating=4.5,
            ),
            Hotel(
                name="Seaside Resort",
                city="Miami",
                country="USA",
                address="456 Ocean Drive, Miami 33139",
                description="Beautiful beachfront resort",
                star_rating=4.0,
            ),
            Hotel(
                name="Mountain View Lodge",
                city="Denver",
                country="USA",
                address="789 Alpine Rd, Denver 80202",
                description="Cozy mountain retreat",
                star_rating=3.5,
            )
        ]

        db.session.add_all(hotels)
        db.session.flush()
        db.session.commit()
        
        count = db.session.execute(text("SELECT COUNT(*) FROM hotels")).scalar()
        app.logger.info(f"✅ Successfully seeded {count} hotels")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    app = create_app()
    ensure_database_setup(app)
    app.run(host='0.0.0.0', port=3000, debug=True)