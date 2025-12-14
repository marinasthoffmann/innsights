# 🏨 InnSight - AI-Powered Hotel Review Analysis

Event-driven microservices architecture for analyzing hotel reviews with AI sentiment analysis.

## 🏗️ Architecture
```
┌─────────────┐
│  Flask API  │ 
└──────┬──────┘
       │ Publishes: ReviewCreated
       ▼
┌──────────────┐
│  RabbitMQ    │ (Queue: review.created)
└──────┬───────┘
       │
       ▼
┌─────────────┐
│  AI Worker  │
└──────┬──────┘
       │ Publishes: AnalysisCompleted
       ▼
┌──────────────┐
│  RabbitMQ    │ (Queue: analysis.completed)
└──────┬───────┘
       │
       ▼
┌─────────────┐
│   Result    │ 
│  Consumer   │
└──────┬──────┘
       ▼
┌─────────────┐
│ PostgreSQL  │
└─────────────┘
```

## ✨ Features

- 🤖 **AI Sentiment Analysis** - BERT-based multilingual sentiment detection
- 📊 **Review Management** - CRUD operations for hotel reviews
- 🏨 **Hotel Management** - Manage hotel information and listings
- 🔄 **Event-Driven** - Asynchronous processing with RabbitMQ
- 🎯 **Microservices** - Clean separation of concerns

## 🛠️ Tech Stack

### Backend
- **Flask** - REST API framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Relational database
- **RabbitMQ** - Message broker
- **Pika** - RabbitMQ client for Python

### AI/ML
- **Transformers** - Hugging Face library
- **BERT** - Pre-trained sentiment analysis model

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/marinasthoffmann/innsights.git
   cd innsight
```

2. **Set up environment variables**   
   Create and edit `.env` and update credentials:
```bash
   POSTGRES_PASSWORD=your_secure_password
   RABBITMQ_DEFAULT_PASS=your_secure_password
```

3. **Start all services**
```bash
   docker-compose up -d
```

4. **Check services are running**
```bash
   docker-compose ps
```

### 🎯 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:5000 | - |
| **API Health** | http://localhost:5000/health | - |
| **RabbitMQ Management** | http://localhost:15672 | guest / guest (change in prod) |

## 📚 API Documentation

### Hotels

#### Get All Hotels
```bash
GET /api/v1/hotels
```

#### Get Hotel by ID
```bash
GET /api/v1/hotels/{id}
```

#### Create Hotel
```bash
POST /api/v1/hotels
Content-Type: application/json

{
  "name": "Grand Hotel",
  "city": "New York",
  "country": "USA",
  "address": "123 Main St",
  "description": "Luxury hotel in downtown",
  "star_rating": 4.5
}
```

### Reviews

#### Get All Reviews
```bash
GET /api/v1/reviews
```

#### Get Review by ID
```bash
GET /api/v1/reviews/{id}
```

#### Create Review (triggers AI analysis)
```bash
POST /api/v1/reviews
Content-Type: application/json

{
  "hotel_id": 1,
  "user_name": "Marina Hoffmann",
  "rating": 5,
  "title": "Excellent stay!",
  "content": "The hotel was amazing! Great service and clean rooms."
}
```

**Response includes AI analysis:**
```json
{
  "id": 1,
  "hotel_id": 1,
  "user_name": "Marina Hoffmann",
  "rating": 5,
  "title": "Excellent stay!",
  "content": "The hotel was amazing!...",
  "status": "COMPLETED",
  "sentiment_score": 0.9,
  "sentiment_label": "positive",
  "created_at": "2025-12-14T10:00:00Z",
  "updated_at": "2025-12-14T10:00:05Z"
}
```

## 📊 System Status

### Check RabbitMQ Queues

1. Open http://localhost:15672
2. Login with credentials from `.env`
3. Navigate to **Queues** tab
4. Monitor:
   - `review.created` - Reviews waiting for AI analysis
   - `analysis.completed` - Results waiting to be saved

## 🏗️ Project Structure
```
innsight/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── schemas/         # Data validation
│   │   ├── queue_publisher.py
│   │   ├── result_consumer.py
│   │   └── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── start_consumer.py
├── ai-worker/
│   ├── worker.py            # AI processing consumer
│   ├── ai_analyzer.py       # Sentiment analysis
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```