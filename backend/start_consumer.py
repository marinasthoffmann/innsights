import sys
import logging

sys.path.insert(0, '/app/app')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    from app import create_app
    from result_consumer import start_consumer
    
    app = create_app()
    
    with app.app_context():
        start_consumer()