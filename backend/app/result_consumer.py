import os
import logging
import pika
import json
from models.review import Review, ReviewStatus
from extensions import db

logger = logging.getLogger(__name__)

def start_consumer():
    """Start consuming analysis results"""
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    queue_name = 'analysis.completed'
    
    logger.info("=" * 60)
    logger.info("📥 Result Consumer - InnSight API")
    logger.info("=" * 60)
    logger.info(f"🔌 Connecting to RabbitMQ: {rabbitmq_host}")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbitmq_host,
            heartbeat=600,
            blocked_connection_timeout=300
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )
    
    logger.info(f"✅ Connected successfully!")
    logger.info(f"👂 Listening on queue: '{queue_name}'")
    logger.info("   Press CTRL+C to exit")
    logger.info("=" * 60)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping consumer...")
        channel.stop_consuming()
    
    connection.close()
    logger.info("👋 Consumer stopped")

def callback(ch, method, properties, body):
    """Callback when analysis result is received"""
    try:
        event = json.loads(body)
        logger.info(f"📨 Received event: {event.get('event_type')}")
        
        if event.get('event_type') == 'AnalysisCompleted':
            review_id = event.get('review_id')
            results = event.get('data')
            
            logger.info(f"🔄 Processing AnalysisCompleted for review {review_id}")

            success = update_review_with_results(review_id, results)
            
            if success:
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info("✅ Event processed and acknowledged")
            else:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                logger.warning("⚠️ Processing failed, event requeued")
        else:
            logger.warning(f"⚠️ Unknown event type: {event.get('event_type')}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    except Exception as e:
        logger.error(f"❌ Error processing event: {e}")
        logger.exception("Full traceback:")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def update_review_with_results(review_id, results):
    """
    Update review in database with AI results
    
    Args:
        review_id: Review ID
        results: AI analysis results
    """
    try:        
        logger.info(f"💾 Updating review {review_id} in database...")

        review = Review.query.get(review_id)
        
        if not review:
            logger.error(f"❌ Review {review_id} not found!")
            return False
        
        # Update with AI results
        review.sentiment_score = results.get('sentiment_score')
        review.sentiment_label = results.get('sentiment_label')
        review.aspects = results.get('aspects')
        review.topics = results.get('topics')
        review.key_phrases = results.get('key_phrases')
        review.status = ReviewStatus.COMPLETED
        
        db.session.commit()
        
        logger.info(f"✅ Review {review_id} updated successfully!")
        logger.info(f"   Sentiment: {review.sentiment_label} ({review.sentiment_score})")
        logger.info(f"   Status: → COMPLETED")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error updating review {review_id}: {e}")
        logger.exception("Full traceback:")
        
        try:
            review.status = ReviewStatus.FAILED
            db.session.commit()
        except:
            pass
        
        return False