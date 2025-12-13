from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

def init_extensions(app):
    """
    Initialize all Flask extensions with the app instance.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", ["*"])}}
    )

    with app.app_context():
        import models.hotel
        import models.review
        app.logger.debug("Models imported and registered")
