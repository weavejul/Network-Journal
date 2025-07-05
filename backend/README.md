# Network Journal Backend

A comprehensive backend system for the Network Journal, a personal intelligence platform for mapping and understanding your professional and personal network. This backend implements a graph-native architecture with AI-powered automation and intelligent data processing.

## 🏗️ Architecture Overview

The backend follows a **modular microservices architecture** with three primary components:

1. **API Gateway** - FastAPI-based REST API with comprehensive routing and middleware
2. **Graph Service** - Neo4j database layer with optimized graph operations
3. **AI Service** - LangChain-powered intelligent automation and data processing

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Graph Service │
│   (React/Svelte)│◄──►│   (FastAPI)     │◄──►│   (Neo4j)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Service    │
                       │   (LangChain)   │
                       └─────────────────┘
```

## 🛠️ Technology Stack

### Core Framework
- **FastAPI 0.104.1** - Modern, fast web framework for building APIs with Python 3.8+
- **Uvicorn 0.24.0** - Lightning-fast ASGI server implementation
- **Pydantic 2.7.4+** - Data validation and settings management using Python type annotations

### Database & Storage
- **Neo4j 5.28.1** - Native graph database for relationship-centric data modeling
- **Redis 5.0.1** - In-memory data structure store for caching and session management
- **APOC Plugin** - Neo4j procedures and utilities for advanced graph operations

### AI & Machine Learning
- **LangChain 0.3.26** - Framework for developing applications with LLMs
- **LangChain OpenAI 0.3.25** - OpenAI integration for GPT models
- **LangChain Community 0.3.26** - Community-maintained integrations
- **OpenAI 1.91.0** - Official OpenAI Python client
- **Anthropic 0.8.1** - Claude model integration

### HTTP & API
- **HTTPX 0.25.2** - Fully featured HTTP client for Python
- **Requests 2.31.0** - HTTP library for Python
- **FastAPI CORS 0.0.6** - CORS middleware for FastAPI
- **SlowAPI 0.1.9** - Rate limiting for FastAPI applications

### Security & Authentication
- **Python-Jose 3.3.0** - JavaScript Object Signing and Encryption implementation
- **Passlib 1.7.4** - Password hashing library with bcrypt support
- **Python-Multipart 0.0.6** - Streaming multipart parser for Python

### Development & Testing
- **Pytest 7.4.3** - Testing framework
- **Pytest-Asyncio 0.21.1** - Async support for pytest
- **Black 23.11.0** - Code formatter
- **Isort 5.12.0** - Import sorting utility
- **Flake8 6.1.0** - Linter
- **MyPy 1.7.1** - Static type checker

### Monitoring & Observability
- **Structlog 23.2.0** - Structured logging for Python
- **Sentry SDK 1.38.0** - Error tracking and performance monitoring

### Utilities
- **Python-Dotenv 1.0.0** - Environment variable management
- **Python-Dateutil 2.8.2** - Date utilities
- **Email-Validator 2.1.0** - Email validation
- **Asyncio-MQTT 0.16.1** - Async MQTT client

## 📁 Project Structure

```
backend/
├── api/                          # FastAPI application
│   ├── main.py                   # Application entry point
│   ├── requirements.txt          # API-specific dependencies
│   └── routers/                  # API route handlers
│       ├── people.py             # Person management endpoints
│       ├── companies.py          # Company management endpoints
│       ├── interactions.py       # Interaction management endpoints
│       ├── topics.py             # Topic management endpoints
│       ├── events.py             # Event management endpoints
│       ├── locations.py          # Location management endpoints
│       ├── graph.py              # Graph query endpoints
│       └── ai.py                 # AI service endpoints
├── graph_service/                # Neo4j database layer
│   ├── connection.py             # Database connection management
│   ├── people.py                 # Person entity operations
│   ├── companies.py              # Company entity operations
│   ├── interactions.py           # Interaction entity operations
│   ├── topics.py                 # Topic entity operations
│   ├── events.py                 # Event entity operations
│   ├── locations.py              # Location entity operations
│   └── graph_queries.py          # Complex graph queries
├── ai_service/                   # AI and automation services
│   ├── note_processor.py         # LLM-powered note processing
│   └── __init__.py
└── ai-service/                   # Alternative AI service structure
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Neo4j Database (local or cloud)
- OpenAI API Key (for AI features)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd network-journal/backend
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables**
   ```env
   # Database Configuration
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   NEO4J_DATABASE=neo4j
   
   # API Configuration
   API_HOST=0.0.0.0
   API_PORT=8000
   API_PREFIX=/api/v1
   DEBUG=true
   
   # AI Configuration
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   DEFAULT_LLM_PROVIDER=openai
   DEFAULT_MODEL=gpt-4o-mini
   
   # Security
   SECRET_KEY=your-secret-key-here
   
   # Redis Configuration
   REDIS_URL=redis://localhost:6379
   ```

### Development Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d neo4j redis
   ```

3. **Run the API server**
   ```bash
   cd api
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Production Deployment

1. **Build Docker images**
   ```bash
   docker-compose build
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🗄️ Database Schema

### Node Labels

The graph database uses the following node labels to represent entities:

- **Person** - Central entity representing individuals in the network
- **Company** - Organizations where people work or have worked
- **Interaction** - Specific events of communication or meetings
- **Topic** - Interests, skills, or concepts discussed
- **Event** - Gatherings like conferences, parties, or meetings
- **Location** - Geographical places

### Relationship Types

- `(:Person)-[:KNOWS]->(:Person)` - General connection between people
- `(:Person)-[:WORKS_AT]->(:Company)` - Employment relationship
- `(:Person)-[:PARTICIPATED_IN]->(:Interaction)` - Person involved in interaction
- `(:Interaction)-[:MENTIONED]->(:Topic)` - Topics discussed in interaction
- `(:Person)-[:INTERESTED_IN]->(:Topic)` - Direct interest link
- `(:Person)-[:ATTENDED]->(:Event)` - Event attendance
- `(:Event)-[:HELD_AT]->(:Location)` - Event location
- `(:Person)-[:LIVES_IN]->(:Location)` - Residence location

### Example Cypher Queries

```cypher
// Find all people who work at the same company
MATCH (p1:Person)-[:WORKS_AT]->(c:Company)<-[:WORKS_AT]-(p2:Person)
WHERE p1 <> p2
RETURN p1.name, p2.name, c.name

// Find people interested in specific topics
MATCH (p:Person)-[:INTERESTED_IN]->(t:Topic)
WHERE t.name IN ['Python', 'Machine Learning']
RETURN p.name, collect(t.name) as interests

// Find interaction path between two people
MATCH path = (p1:Person)-[:KNOWS*1..3]-(p2:Person)
WHERE p1.name = 'John Doe' AND p2.name = 'Jane Smith'
RETURN path
```

## 🤖 AI Services

### Note Processor Service

The `NoteProcessorService` uses LangChain and OpenAI to extract structured information from unstructured user notes.

**Key Features:**
- Named Entity Recognition (NER) for people, companies, topics
- Relationship extraction and strength assessment
- Event and location identification
- Confidence scoring for extracted data
- Support for complex relationships and additional entities

**Example Usage:**
```python
from backend.ai_service.note_processor import NoteProcessorService

processor = NoteProcessorService()
result = await processor.process_note(
    "Met Jane Doe at the AI Summit. She's a Product Manager at Google "
    "working on generative models. We talked about hiking and trail running."
)
```

**Extracted Output:**
```json
{
  "person_name": "Jane Doe",
  "company": "Google",
  "role": "Product Manager",
  "topics_of_interest": ["hiking", "trail running"],
  "events_mentioned": ["AI Summit"],
  "location": null,
  "confidence_score": 0.9
}
```

### LangChain Integration

The AI service leverages LangChain's powerful features:

- **ChatPromptTemplate** - Structured prompting with examples
- **JsonOutputParser** - Reliable JSON output parsing
- **ChatOpenAI** - OpenAI model integration
- **Chain Composition** - Modular AI workflows

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/people` | List all people |
| POST | `/api/v1/people` | Create a new person |
| GET | `/api/v1/people/{id}` | Get person details |
| PUT | `/api/v1/people/{id}` | Update person |
| DELETE | `/api/v1/people/{id}` | Delete person |
| GET | `/api/v1/graph/network` | Get network visualization data |
| POST | `/api/v1/ai/process-note` | Process unstructured note |

### Graph Query Endpoints

- `GET /api/v1/graph/network` - Get complete network data
- `GET /api/v1/graph/path/{start_id}/{end_id}` - Find path between nodes
- `GET /api/v1/graph/community/{node_id}` - Find community around node
- `GET /api/v1/graph/recommendations/{person_id}` - Get recommendations

### AI Service Endpoints

- `POST /api/v1/ai/process-note` - Process unstructured notes
- `POST /api/v1/ai/suggest-updates` - Get AI suggestions for contacts
- `GET /api/v1/ai/status` - Check AI service status

## 🔧 Configuration

### Settings Management

The application uses Pydantic Settings for configuration management:

```python
from shared.config import get_settings

settings = get_settings()
```

**Key Configuration Categories:**

1. **Database Configuration**
   - Neo4j connection parameters
   - Redis cache settings

2. **API Configuration**
   - Host, port, and prefix settings
   - CORS configuration
   - Rate limiting parameters

3. **AI Configuration**
   - LLM provider selection
   - Model parameters
   - API keys

4. **Security Configuration**
   - Secret keys
   - Token expiration
   - Authentication settings

### Environment Variables

All configuration is managed through environment variables with sensible defaults:

```bash
# Required for AI features
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"

# Database configuration
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"

# API configuration
export API_HOST="0.0.0.0"
export API_PORT="8000"
export DEBUG="true"
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_people.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── test_people.py        # Person entity tests
├── test_companies.py     # Company entity tests
├── test_interactions.py  # Interaction entity tests
├── test_topics.py        # Topic entity tests
├── test_events.py        # Event entity tests
├── test_locations.py     # Location entity tests
└── test_graph_queries.py # Graph query tests
```

### Test Database

Tests use a separate test database to avoid affecting development data:

```python
# Test configuration
NEO4J_DATABASE=test
REDIS_URL=redis://localhost:6379/1
```

## 📊 Monitoring & Logging

### Structured Logging

The application uses Structlog for structured logging:

```python
from shared.utils import setup_logging

logger = setup_logging(__name__)
logger.info("Processing request", user_id=123, action="create_person")
```

### Health Checks

- `GET /health` - Basic health check endpoint
- Database connectivity verification
- AI service status check

### Error Tracking

Sentry integration for error tracking and performance monitoring:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()]
)
```

## 🔒 Security Features

### Rate Limiting

SlowAPI integration provides rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/people")
@limiter.limit("100/hour")
async def get_people(request: Request):
    # Implementation
```

### CORS Configuration

Configurable CORS middleware for frontend integration:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Input Validation

Pydantic models ensure data validation:

```python
from pydantic import BaseModel, EmailStr

class PersonCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None
```

## 🚀 Performance Optimization

### Database Optimization

1. **Indexing Strategy**
   ```cypher
   CREATE INDEX person_name_index FOR (p:Person) ON (p.name);
   CREATE INDEX company_name_index FOR (c:Company) ON (c.name);
   ```

2. **Query Optimization**
   - Use parameterized queries
   - Implement pagination
   - Cache frequently accessed data

### Caching Strategy

Redis caching for:
- Graph query results
- AI processing results
- User session data
- Frequently accessed entities

### Async Operations

Full async/await support for:
- Database operations
- AI service calls
- External API requests
- File processing

## 🔄 CI/CD Pipeline

### Development Workflow

1. **Code Quality Checks**
   ```bash
   black backend/
   isort backend/
   flake8 backend/
   mypy backend/
   ```

2. **Testing**
   ```bash
   pytest backend/tests/
   ```

3. **Docker Build**
   ```bash
   docker-compose build api
   ```

### Production Deployment

1. **Environment Setup**
   - Configure production environment variables
   - Set up monitoring and logging
   - Configure SSL certificates

2. **Database Migration**
   - Backup existing data
   - Run schema updates
   - Verify data integrity

3. **Service Deployment**
   - Deploy with Docker Compose
   - Health check verification
   - Rollback procedures

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: `/docs` - Interactive API documentation
- **ReDoc**: `/redoc` - Alternative documentation format
- **OpenAPI Schema**: `/openapi.json` - Machine-readable schema

### Code Examples

```python
import httpx

# Create a new person
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/people",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "company": "Tech Corp",
            "role": "Software Engineer"
        }
    )
    person = response.json()

# Process a note with AI
response = await client.post(
    "http://localhost:8000/api/v1/ai/process-note",
    json={"note_text": "Met Jane at the conference..."}
)
result = response.json()
```

## 🤝 Contributing

### Development Guidelines

1. **Code Style**
   - Follow PEP 8 guidelines
   - Use Black for code formatting
   - Use isort for import sorting

2. **Testing**
   - Write tests for new features
   - Maintain test coverage above 80%
   - Use descriptive test names

3. **Documentation**
   - Update API documentation
   - Add docstrings to functions
   - Update this README for significant changes

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the API documentation at `/docs`
2. Review the test files for usage examples
3. Open an issue on GitHub
4. Contact the development team

---

**Network Journal Backend** - Building intelligent networks, one connection at a time. 