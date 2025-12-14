import os
import sys
import pika
import json
from loguru import logger
from ai_analyzer import get_analyzer

logger.remove()
logger.add(sys.stdout, level="INFO")

def start_consumer():
    """Start the consumer"""
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    queue_name = 'review.created'
    
    logger.info("=" * 50)
    logger.info("🐰 Review Consumer - InnSight")
    logger.info("=" * 50)
    logger.info(f"🔌 Connecting to RabbitMQ: {rabbitmq_host}")
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host)
    )
    channel = connection.channel()
    
    channel.queue_declare(queue=queue_name, durable=True)
    
    # Configure QoS (process 1 at a time)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=callback,
        auto_ack=False
    )
    
    logger.info(f"👂 Waiting for reviews in queue '{queue_name}'...")
    logger.info("   Press CTRL+C to exit")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping consumer...")
        channel.stop_consuming()
    
    connection.close()
    logger.info("👋 Consumer stopped")


def callback(ch, method, properties, body):
    """Callback when message is received"""
    try:
        message = json.loads(body)
        logger.info(f"📨 New message received!")

        success = process_review(message)
        
        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("✅ Message acknowledged (ACK)")
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logger.warning("⚠️ Processing failed, message requeued")
            
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def process_review(review_data):
    """
    Process review with AI analysis (NO database access)
    
    Args:
        review_data: Review data from queue
    
    Returns:
        bool: True if processed successfully
    """
    review_id = review_data.get('review_id')
    title = review_data.get('title')
    content = review_data.get('content')
    rating = review_data.get('rating')
    
    try:
        logger.info(f"🔄 Processing review {review_id}")
        logger.info(f"   Title: {title}...")
        logger.info(f"   Content: {content[:100]}...")
        logger.info(f"   Rating: {rating} stars")

        analyzer = get_analyzer()

        logger.info("🔍 Analyzing sentiment...")
        sentiment = analyzer.analyze(content, rating)
        
        logger.info(f"✅ Analysis complete!")
        logger.info(f"   Sentiment: {sentiment['sentiment_label']} ({sentiment['sentiment_score']})")

        result = {
            'sentiment_score': sentiment['sentiment_score'],
            'sentiment_label': sentiment['sentiment_label'],
            # TODO: Add more analysis later
            'aspects': None,
            'topics': None,
            'key_phrases': None
        }
        
        # Publish result to queue
        success = publish_result(review_id, result)
        
        if success:
            logger.info(f"✅ Review {review_id} processed and result published!")
            return True
        else:
            logger.error(f"❌ Failed to publish result for review {review_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error processing review {review_id}: {e}")
        logger.exception("Full traceback:")
        return False
    
def publish_result(review_id, analysis_result):
    """
    Publish analysis result back to RabbitMQ
    
    Args:
        review_id: Review ID
        analysis_result: AI analysis results
    
    Returns:
        bool: True if published successfully
    """
    try:
        rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=rabbitmq_host)
        )
        channel = connection.channel()

        result_queue = 'analysis.completed'
        channel.queue_declare(queue=result_queue, durable=True)

        event = {
            'event_type': 'AnalysisCompleted',
            'review_id': review_id,
            'data': analysis_result
        }

        channel.basic_publish(
            exchange='',
            routing_key=result_queue,
            body=json.dumps(event),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type='application/json'
            )
        )
        
        logger.info(f"📤 Published result to '{result_queue}' queue")
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to publish result: {e}")
        return False

if __name__ == '__main__':
    start_consumer()