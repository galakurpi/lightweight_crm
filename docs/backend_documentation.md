# Backend Documentation - Lightweight CRM

## Overview

The backend is a Django 4.2.23 REST API application providing comprehensive CRM with AI-powered chat capabilities. Architecture includes RESTful endpoints for lead management, Supabase database integration, OpenAI chat assistant with function calling, and Celery asynchronous task processing.

## Architecture

### Tech Stack
- **Django**: 4.2.23 - Main web framework
- **Django REST Framework**: 3.14.0 - API development
- **Supabase**: 2.4.2 - PostgreSQL database service
- **OpenAI**: 1.12.0 - AI chat integration with function calling
- **Celery**: 5.3.4 - Asynchronous task processing
- **Redis**: 5.0.1 - Message broker for Celery

### Project Structure
```
backend/
├── settings.py               # Django configuration and environment settings
├── urls.py                   # Main URL routing configuration
├── celery_app.py            # Celery configuration and task discovery
└── api/
    ├── views.py             # API endpoint implementations
    ├── urls.py              # API URL routing
    ├── supabase_client.py   # Database service layer
    ├── chat_service.py      # OpenAI integration and AI logic
    ├── tasks.py             # Celery background tasks
    └── tests.py             # Unit tests
```

## Core Components

### Django Settings (settings.py)
Central configuration managing database (Supabase), CORS (React frontend), sessions (chat context), OpenAI API, and Celery (Redis broker).

**Environment Variables:**
```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
SUPABASE_URL = config('SUPABASE_URL')
SUPABASE_KEY = config('SUPABASE_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
```

### API Views (views.py)
RESTful endpoints handling all CRM operations:

**Lead Management:**
1. **Leads List** (`/leads/`) - GET: grouped by status, POST: create with ordering
2. **Lead Detail** (`/leads/<id>/`) - GET: retrieve, PUT: update, DELETE: remove
3. **Lead Status** (`/leads/<id>/status/`) - PUT: update status and card order

**Chat Assistant:**
4. **Chat Message** (`/chat/`) - POST: initiate async processing, returns task_id
5. **Chat Status** (`/chat/status/<task_id>/`) - GET: poll for completion (PENDING/PROCESSING/SUCCESS/FAILURE)
6. **Clear Chat** (`/chat/clear/`) - POST: clear conversation context

### Database Service (supabase_client.py)
Service layer with lazy loading, error handling, and connection management.

**Core Methods:**
```python
class SupabaseService:
    @staticmethod
    def get_all_leads() -> List[Dict]
    def create_lead(lead_data: Dict) -> Optional[Dict]
    def update_lead(lead_id: str, lead_data: Dict) -> Optional[Dict]
    def delete_lead(lead_id: str) -> bool
    def get_lead_by_id(lead_id: str) -> Optional[Dict]
```

**Schema:** id (UUID), name, company, email, phone, value, notes, status, source, card_order, created_at, updated_at

### AI Chat Service (chat_service.py)
OpenAI integration with session-based context, function calling, intent routing, and fuzzy lead matching.

**OpenAI Functions:**
- `search_leads`, `update_lead_status`, `update_lead_data`, `create_lead`, `delete_lead`

**Context Management:**
```python
def get_conversation_context(self, session_key: str) -> List[Dict]
def update_conversation_context(self, session_key: str, message: Dict)
def clear_conversation_context(self, session_key: str)
```

### Async Task Processing (tasks.py)
Celery background tasks for AI processing:

```python
@shared_task(bind=True)
def process_chat_message(self, message, session_key, conversation_context=None):
    # Update task status, fetch leads, process through ChatService
    # Return AI response and operation results
```

**States:** PENDING → PROCESSING → SUCCESS/FAILURE

## API Endpoints Reference

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET/POST | `/leads/` | List/create leads | Lead data | Kanban structure/Created lead |
| GET/PUT/DELETE | `/leads/{id}/` | Lead operations | Lead data | Lead object/204 |
| PUT | `/leads/{id}/status/` | Update status | `{status, card_order}` | Updated lead |
| POST | `/chat/` | Send message | `{message}` | `{task_id, status}` |
| GET | `/chat/status/{task_id}/` | Poll status | None | Task state/results |
| POST | `/chat/clear/` | Clear conversation | None | Success confirmation |
| GET | `/test/` | Health check | None | `{message, status}` |

## Data Models

### Lead Structure
```json
{
  "id": "uuid-string", "name": "John Smith", "company": "Tech Corp",
  "email": "john@techcorp.com", "phone": "+1-555-0123", "value": 50000.00,
  "notes": "Interested in enterprise solution", "status": "Meeting booked",
  "source": "Website", "card_order": 1,
  "created_at": "2024-01-15T10:30:00Z", "updated_at": "2024-01-15T14:45:00Z"
}
```

### Chat Message Structure
```json
{
  "message": "Move John Smith to closed win",
  "session_key": "django-session-key",
  "context": [{"role": "user", "content": "Previous message"}]
}
```

## Authentication & Security

### Session Management
Django sessions for chat context, database-backed storage, 24-hour expiration

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ALLOW_CREDENTIALS = True
```

### Environment Security
Django secret, API keys (OpenAI/Supabase), configurable debug mode

## Error Handling

**HTTP Status Codes:** 200 (OK), 201 (Created), 204 (No Content), 400 (Bad Request), 404 (Not Found), 500 (Server Error)

**Error Format:**
```json
{
  "error": "Human-readable message",
  "details": "Technical details (optional)"
}
```

**Error Types:** Connection failures (graceful degradation), query errors (logged with user-friendly messages), OpenAI API errors (rate limiting, service unavailable), function call errors

## Configuration

**Required Environment Variables:**
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# AI
OPENAI_API_KEY=sk-your-openai-api-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Deployment

### Development Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Edit with credentials
python manage.py migrate
python manage.py runserver
celery -A backend worker --loglevel=info  # Separate terminal
```

### Production Considerations
WSGI/ASGI server configuration, static file serving, production database settings, environment variables

## Testing

**Test Types:** Unit tests (functions/methods), integration tests (API endpoints), service tests (database/external), mock testing (OpenAI/Supabase)

**Commands:**
```bash
python manage.py test                    # All tests
python manage.py test backend.api.tests # Specific file
coverage run --source='.' manage.py test && coverage report  # With coverage
```

## Troubleshooting

**Common Issues:**
1. **Database:** Check SUPABASE_URL/KEY environment variables
2. **OpenAI:** Verify OPENAI_API_KEY
3. **Celery:** Test Redis connection with `redis-cli ping`, monitor with `celery -A backend events`
4. **CORS:** Verify CORS_ALLOWED_ORIGINS includes frontend URL

## API Usage Examples

### Creating Lead
```python
import requests
response = requests.post("http://localhost:8000/leads/", json={
    "name": "Jane Doe", "company": "Example Corp", "email": "jane@example.com",
    "phone": "+1-555-0199", "value": 75000, "status": "Interest", "source": "Website"
})
```

### Chat Interaction
```python
# Send message
response = requests.post("http://localhost:8000/chat/", 
                        json={"message": "Move Jane Doe to meeting booked"})
task_id = response.json()["task_id"]

# Poll for completion
while True:
    status = requests.get(f"http://localhost:8000/chat/status/{task_id}/").json()
    if status["state"] == "SUCCESS":
        print(status["result"]["ai_message"])
        break
    elif status["state"] == "FAILURE":
        print("Error:", status["error"])
        break
    time.sleep(2)
```

## Future Enhancements

**Improvements:** User authentication/authorization, role-based permissions, webhooks for lead changes, bulk operations, full-text search, pipeline analytics, email integration

**Architecture:** Microservices decomposition, event sourcing, GraphQL API, WebSockets for real-time, advanced caching strategies

## Contributing

**Code Style:** PEP 8 compliance, type hints, comprehensive docstrings, clear comments

**Workflow:** Feature branch → Environment setup → Testing → Documentation → Code review → Integration

This documentation enables developers and AI assistants to effectively work with and extend the CRM API system.