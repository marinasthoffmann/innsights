import logging
import random
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy import inspect

from config import get_config
from extensions import init_extensions, db
from routes.health_bp import health_bp
from routes.hotels_bp import hotels_bp
from routes.reviews_bp import reviews_bp
from models.hotel import Hotel
from models.review import Review, ReviewStatus


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
            # US Hotels
            Hotel(name="Grand Plaza Hotel", city="New York", country="USA",
                  address="123 Main St, NY 10001", 
                  description="Luxury hotel in the heart of Manhattan", star_rating=4.5),
            Hotel(name="Seaside Resort", city="Miami", country="USA",
                  address="456 Ocean Drive, Miami 33139", 
                  description="Beautiful beachfront resort", star_rating=4.0),
            Hotel(name="Mountain View Lodge", city="Denver", country="USA",
                  address="789 Alpine Rd, Denver 80202", 
                  description="Cozy mountain retreat", star_rating=3.5),
            Hotel(name="Downtown Business Hotel", city="Chicago", country="USA",
                  address="321 Commerce Blvd, Chicago 60601", 
                  description="Modern business hotel", star_rating=4.0),
            Hotel(name="Historic Inn", city="Boston", country="USA",
                  address="555 Heritage Lane, Boston 02101", 
                  description="Charming historic inn", star_rating=3.8),
            
            # European Hotels
            Hotel(name="Royal Palace Hotel", city="London", country="UK",
                  address="10 Buckingham Road, London SW1A 1AA",
                  description="Elegant hotel near royal landmarks", star_rating=5.0),
            Hotel(name="Seine View Hotel", city="Paris", country="France",
                  address="25 Rue de Rivoli, Paris 75001",
                  description="Boutique hotel with Eiffel Tower views", star_rating=4.7),
            Hotel(name="Berlin Central Hotel", city="Berlin", country="Germany",
                  address="15 Unter den Linden, Berlin 10117",
                  description="Modern hotel in city center", star_rating=4.2),
            Hotel(name="Rome Heritage Hotel", city="Rome", country="Italy",
                  address="88 Via del Corso, Rome 00186",
                  description="Classic Italian hotel near Colosseum", star_rating=4.5),
            Hotel(name="Barcelona Beach Resort", city="Barcelona", country="Spain",
                  address="42 Passeig de Gracia, Barcelona 08007",
                  description="Mediterranean resort with beach access", star_rating=4.3),
            
            # Asian Hotels
            Hotel(name="Tokyo Tower Hotel", city="Tokyo", country="Japan",
                  address="1-1-1 Shibuya, Tokyo 150-0002",
                  description="High-tech hotel in heart of Tokyo", star_rating=4.6),
            Hotel(name="Singapore Marina Hotel", city="Singapore", country="Singapore",
                  address="10 Marina Bay, Singapore 018956",
                  description="Luxury waterfront hotel", star_rating=4.8),
            Hotel(name="Hong Kong Skyline Hotel", city="Hong Kong", country="China",
                  address="88 Nathan Road, Hong Kong",
                  description="Modern hotel with harbor views", star_rating=4.4),
            Hotel(name="Bangkok Palace Hotel", city="Bangkok", country="Thailand",
                  address="123 Sukhumvit Road, Bangkok 10110",
                  description="Traditional Thai hospitality", star_rating=4.1),
            Hotel(name="Dubai Luxury Resort", city="Dubai", country="UAE",
                  address="1 Sheikh Zayed Road, Dubai",
                  description="Ultra-luxury resort", star_rating=5.0),
        ]

        db.session.add_all(hotels)
        db.session.flush()

        review_data = [
            ("Alice Johnson", 5, "Absolutely perfect!",
             "This hotel exceeded all expectations. Room was spotless, staff incredibly friendly."),
            ("Bob Smith", 4, "Great stay overall",
             "Really enjoyed our stay. Excellent amenities and great breakfast buffet."),
            ("Carol White", 5, "Amazing experience",
             "From check-in to check-out, everything was seamless. Highly recommend!"),
            ("David Brown", 3, "Decent but not great",
             "Good location and clean rooms, but felt a bit dated. AC was noisy."),
            ("Emma Davis", 4, "Good value for money",
             "For the price, great value. Modern gym facilities. Good for business."),
            ("Frank Miller", 5, "Perfect family vacation",
             "Perfect with kids. Amazing pool, great staff, spacious family suite."),
            ("Grace Lee", 2, "Disappointed",
             "Didn't live up to photos. Room smaller than expected, construction noise."),
            ("Henry Wilson", 4, "Pleasant surprise",
             "Exceeded expectations. Rooftop bar has incredible views, very comfortable bed."),
            ("Isabel Martinez", 5, "Best hotel in the city!",
             "Hands down the best. Every detail perfect. Fantastic spa!"),
            ("Jack Thompson", 3, "Average experience",
             "Decent but nothing special. Clean, friendly staff, limited breakfast options."),
        ]
        
        # Create unique reviews for each hotel (no duplicates per hotel)
        reviews = []
        for hotel in hotels:
            num_reviews = random.randint(3, 7)

            shuffled_templates = review_data.copy()
            random.shuffle(shuffled_templates)
            selected_templates = shuffled_templates[:num_reviews]

            for template in selected_templates:
                review = Review(
                    hotel_id=hotel.id,
                    user_name=template[0],
                    rating=template[1],
                    title=template[2],
                    content=template[3],
                    status=ReviewStatus.PENDING
                )
                reviews.append(review)
        
        db.session.add_all(reviews)
        db.session.flush()
        db.session.commit()
        
        hotel_count = db.session.execute(text("SELECT COUNT(*) FROM hotels")).scalar()
        review_count = db.session.execute(text("SELECT COUNT(*) FROM reviews")).scalar()

        app.logger.info(f"✅ Successfully seeded {hotel_count} hotels")
        app.logger.info(f"✅ Successfully seeded {review_count} hotels")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    app = create_app()
    ensure_database_setup(app)
    app.run(host='0.0.0.0', port=5000, debug=True)