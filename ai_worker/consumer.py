import os
import sys
from loguru import logger
import pika
import json
import time

logger.remove()
logger.add(sys.stdout, level="INFO")

def start_consumer():
    """Start the consumer"""
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    queue_name = 'review_analysis'
    
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
            # Acknowledge processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("✅ Message acknowledged (ACK)")
        else:
            # Reject and requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            logger.warning("⚠️ Processing failed, message requeued")
            
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def process_review(review_data):
    """
    Process a review
    
    Args:
        review_data: Review data
    """
    review_id = review_data.get('review_id')
    title = review_data.get('title')
    content = review_data.get('content')
    rating = review_data.get('rating')
    
    logger.info(f"🔄 Processing review {review_id}")
    logger.info(f"   title: {title}...")
    logger.info(f"   Content: {content[:50]}...")
    logger.info(f"   Rating: {rating}")
    
    # TODO: AI analysis will be added here!
    # For now, just simulating processing

    time.sleep(2)  # Simulate processing
    
    logger.info(f"✅ Review {review_id} processed successfully!")
    return True

if __name__ == '__main__':
    start_consumer()