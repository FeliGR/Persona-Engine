# Persona Engine

A RESTful API service for managing user personality profiles based on the Big Five personality model.

## Features

- **Personality Management**: Create, retrieve, and update user personas with Big Five traits (openness, conscientiousness, extraversion, agreeableness, neuroticism)
- **REST API**: Clean RESTful endpoints for persona operations with proper validation and error handling
- **Database Integration**: SQLAlchemy ORM with PostgreSQL support and automatic migrations
- **Voice Configuration**: Text-to-speech configuration models with multilingual support
- **Clean Architecture**: Domain-driven design with separation of concerns across repositories, use cases, and controllers
- **Production Ready**: Rate limiting, structured logging, health checks, and monitoring capabilities

## Quick Start

```bash
git clone https://github.com/your-username/persona-engine.git
cd persona-engine
pip install -r requirements.txt
python -m flask run
```

## Configuration

Create a `.env` file:

```env
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here
DB_URI=postgresql://username:password@localhost:5432/persona_db
API_RATE_LIMIT=100
CORS_ORIGINS=*
HOST=0.0.0.0
PORT=5001
```

### Database Setup

The application supports PostgreSQL by default. For development, you can use SQLite:

```env
DB_URI=sqlite:///persona.db
```

## Docker

```bash
docker-compose up -d
```

This will start both the Persona Engine service and a PostgreSQL database with automatic health checks.

## API Endpoints

- `GET /` - Service information and health status
- `GET /health` - Health check endpoint
- `GET /api/personas/<user_id>` - Retrieve a persona by user ID
- `POST /api/personas/` - Create or retrieve a persona
- `PUT /api/personas/<user_id>` - Update persona traits

### Example Usage

Create a persona:
```bash
curl -X POST http://localhost:5001/api/personas/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```

Update a trait:
```bash
curl -X PUT http://localhost:5001/api/personas/user123 \
  -H "Content-Type: application/json" \
  -d '{"trait": "openness", "value": 4.5}'
```

## Tech Stack

- Flask 2.3.3
- SQLAlchemy 2.0.23
- PostgreSQL with psycopg2
- Marshmallow for validation
- Gunicorn for production
- Structlog for logging
- Prometheus metrics
- Docker & Docker Compose 