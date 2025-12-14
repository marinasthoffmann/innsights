import os
import pika
import json
import logging

logger = logging.getLogger(__name__)

class ReviewQueuePublisher:
    """Publishes reviews to RabbitMQ for processing"""

    def __init__(self):
        self.host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.queue_name = 'review.created'
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            self.channel = self.connection.channel()
            
            self.channel.queue_declare(
                queue=self.queue_name,
                durable=True 
            )
            
            logger.info(f"✅ Connected to RabbitMQ: {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error connecting to RabbitMQ: {e}")
            return False
        
    def publish_review(self, review_id, review_data):
        """
        Publish ReviewCreated event
        
        Args:
            review_id: Review ID
            review_data: Review data (content, rating, etc)
        """
        try:
            if not self.channel or self.channel.is_closed:
                self.connect()

            event = {
                'event_type': 'ReviewCreated',
                'review_id': review_id,
                'title': review_data.get('title'),
                'content': review_data.get('content'),
                'rating': review_data.get('rating'),
                'hotel_id': review_data.get('hotel_id')
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(event),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"📤 Published ReviewCreated event for review {review_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing review {review_id}: {e}")
            return False
        
    def close(self):
        """Close connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()

# Global instance (singleton)
_publisher = None

def get_publisher():
    """Returns publisher instance"""
    global _publisher
    if _publisher is None:
        _publisher = ReviewQueuePublisher()
        _publisher.connect()
    return _publisher