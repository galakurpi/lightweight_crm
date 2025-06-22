# Backend Documentation - Lightweight CRM

## Overview

The backend is a Django REST API application built with Django 4.2.23 that provides a comprehensive CRM system with AI-powered chat capabilities. The architecture includes RESTful API endpoints for lead management, Supabase database integration, OpenAI-powered chat assistant with function calling, asynchronous task processing via Celery, and session-based conversation management.

## Architecture

### Tech Stack
- **Django**: 4.2.23 - Main web framework
- **Django REST Framework**: 3.14.0 - API development
- **Supabase**: 2.4.2 - PostgreSQL database service
- **OpenAI**: 1.12.0 - AI chat integration with function calling
- **Celery**: 5.3.4 - Asynchronous task processing
- **Redis**: 5.0.1 - Message broker for Celery
- **HTTPX**: 0.26.0 - HTTP client for API calls
- **Python Decouple**: 3.8 - Environment configuration

### Project Structure
```
backend/
├── __init__.py               # Django project package
├── settings.py               # Django configuration and environment settings
├── urls.py                   # Main URL routing configuration
├── wsgi.py                   # WSGI application entry point
├── asgi.py                   # ASGI application entry point (async support)
├── celery_app.py            # Celery configuration and task discovery
└── api/
    ├── __init__.py          # API app package
    ├── apps.py              # Django app configuration
    ├── admin.py             # Django admin configuration
    ├── views.py             # API endpoint implementations
    ├── urls.py              # API URL routing
    ├── supabase_client.py   # Database service layer
    ├── chat_service.py      # OpenAI integration and AI logic
    ├── tasks.py             # Celery background tasks
    ├── tests.py             # Unit tests
    └── migrations/          # Database migrations
```

## Core Components

### Django Settings (settings.py)
Central configuration file managing all application settings:

**Key Configuration Areas:**
- **Database**: Supabase PostgreSQL integration
- **CORS**: Cross-origin resource sharing for React frontend
- **Sessions**: Django session framework for chat context
- **OpenAI**: API key configuration for AI services
- **Celery**: Redis broker configuration for async tasks
- **Security**: Secret key, debug mode, allowed hosts

**Environment Variables:**
```python
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=True, cast=bool)
SUPABASE_URL = config('SUPABASE_URL')
SUPABASE_KEY = config('SUPABASE_KEY')
OPENAI_API_KEY = config('OPENAI_API_KEY')
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
```

**Installed Apps:**
- `django.contrib.*` - Core Django functionality
- `rest_framework` - DRF for API development
- `corsheaders` - CORS handling for frontend
- `backend.api` - Main application logic

### API Views (views.py)
RESTful API endpoints handling all CRM operations:

#### Lead Management Endpoints

**1. Leads List (`/leads/`)**
- **GET**: Returns all leads grouped by status for Kanban board
- **POST**: Creates new lead with automatic ordering

```python
@api_view(['GET', 'POST'])
def leads_list(request):
    # GET: Group leads by status for Kanban display
    # POST: Create new lead with default status and ordering
```

**2. Lead Detail (`/leads/<lead_id>/`)**
- **GET**: Retrieve specific lead by ID
- **PUT**: Update lead information
- **DELETE**: Remove lead from system

**3. Lead Status Update (`/leads/<lead_id>/status/`)**
- **PUT**: Update lead status and card order (drag & drop support)

#### Chat Assistant Endpoints

**4. Chat Message (`/chat/`)**
- **POST**: Initiate async chat message processing
- Returns task_id for polling status

**5. Chat Status (`/chat/status/<task_id>/`)**
- **GET**: Poll for async task completion and results
- Supports task states: PENDING, PROCESSING, SUCCESS, FAILURE

**6. Clear Chat (`/chat/clear/`)**
- **POST**: Clear conversation context from session

### Database Service (supabase_client.py)
Service layer managing all database operations with Supabase:

**Key Features:**
- **Lazy Loading**: Client initialization on first use
- **Error Handling**: Graceful degradation when database unavailable
- **Connection Management**: Single client instance with global access
- **Credential Validation**: Checks for proper configuration

**Core Methods:**
```python
class SupabaseService:
    @staticmethod
    def get_all_leads() -> List[Dict]
    
    @staticmethod
    def create_lead(lead_data: Dict) -> Optional[Dict]
    
    @staticmethod
    def update_lead(lead_id: str, lead_data: Dict) -> Optional[Dict]
    
    @staticmethod
    def delete_lead(lead_id: str) -> bool
    
    @staticmethod
    def get_lead_by_id(lead_id: str) -> Optional[Dict]
```

**Database Schema (Supabase leads table):**
- `id` (UUID, Primary Key) - Unique lead identifier
- `name` (String) - Lead contact name
- `company` (String) - Organization name
- `email` (String) - Contact email address
- `phone` (String) - Contact phone number
- `value` (Numeric) - Deal value in dollars
- `notes` (Text) - Additional information
- `status` (String) - Pipeline stage (Interest, Meeting booked, etc.)
- `source` (String) - Lead origin
- `card_order` (Integer) - Position within status column
- `created_at` (Timestamp) - Record creation time
- `updated_at` (Timestamp) - Last modification time

### AI Chat Service (chat_service.py)
Comprehensive OpenAI integration with function calling capabilities:

**Architecture:**
- **Session-based Context**: Conversation memory via Django sessions
- **Function Calling**: Structured AI interactions with lead operations
- **Intent Routing**: Automatic classification of user requests
- **Lead Matching**: Fuzzy search and identification logic

**Key Components:**

**1. Conversation Context Management**
```python
def get_conversation_context(self, session_key: str) -> List[Dict]
def update_conversation_context(self, session_key: str, message: Dict)
def clear_conversation_context(self, session_key: str)
```

**2. OpenAI Function Definitions**
- `search_leads` - Find leads by name, company, or email
- `update_lead_status` - Change lead pipeline stage
- `update_lead_data` - Modify specific lead fields
- `create_lead` - Add new lead to system
- `delete_lead` - Remove lead (with confirmation)

**3. Lead Matching Algorithm**
```python
def find_matching_leads(self, query: str, leads: List[Dict]) -> List[Dict]:
    # Fuzzy matching on name, company, email
    # Partial word matching
    # Case-insensitive search
    # Relevance scoring
```

**4. Function Execution Engine**
```python
def execute_function_call(self, function_name: str, arguments: Dict, leads: List[Dict]) -> Dict:
    # Route function calls to appropriate handlers
    # Execute lead operations via SupabaseService
    # Return structured results
```

### Async Task Processing (tasks.py)
Celery background tasks for handling AI processing:

**Main Task:**
```python
@shared_task(bind=True)
def process_chat_message(self, message, session_key, conversation_context=None):
    # Update task status for frontend polling
    # Fetch current leads for context
    # Process message through ChatService
    # Return AI response and operation results
```

**Task States:**
- **PENDING**: Task queued but not started
- **PROCESSING**: Task actively running
- **SUCCESS**: Task completed successfully
- **FAILURE**: Task encountered error

### Celery Configuration (celery_app.py)
Async task processing setup:

**Configuration:**
- **Broker**: Redis for task queue management
- **Result Backend**: Redis for storing task results
- **Serialization**: JSON for task data
- **Auto-discovery**: Automatic task detection from Django apps
- **Time Limits**: 30-minute task timeout

## API Endpoints Reference

### Lead Management

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/leads/` | Get all leads grouped by status | None | Kanban data structure |
| POST | `/leads/` | Create new lead | Lead data object | Created lead object |
| GET | `/leads/{id}/` | Get specific lead | None | Lead object |
| PUT | `/leads/{id}/` | Update lead | Updated lead data | Updated lead object |
| DELETE | `/leads/{id}/` | Delete lead | None | 204 No Content |
| PUT | `/leads/{id}/status/` | Update lead status | `{status, card_order}` | Updated lead object |

### Chat Assistant

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/chat/` | Send chat message | `{message}` | `{task_id, status}` |
| GET | `/chat/status/{task_id}/` | Poll task status | None | Task state and results |
| POST | `/chat/clear/` | Clear conversation | None | Success confirmation |

### Utility

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/test/` | API health check | None | `{message, status}` |

## Data Models

### Lead Model Structure
```json
{
  "id": "uuid-string",
  "name": "John Smith",
  "company": "Tech Corp",
  "email": "john@techcorp.com",
  "phone": "+1-555-0123",
  "value": 50000.00,
  "notes": "Interested in enterprise solution",
  "status": "Meeting booked",
  "source": "Website",
  "card_order": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:45:00Z"
}
```

### Chat Message Structure
```json
{
  "message": "Move John Smith to closed win",
  "session_key": "django-session-key",
  "context": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant",
      "content": "Previous response"
    }
  ]
}
```

## Authentication & Security

### Session Management
- **Django Sessions**: Built-in session framework for chat context
- **Session Storage**: Database-backed session storage
- **Session Lifecycle**: 24-hour expiration, persistent across requests
- **Security**: CSRF protection, secure session cookies

### CORS Configuration
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True  # For session cookies
```

### Environment Security
- **Secret Key**: Django secret key from environment
- **API Keys**: OpenAI and Supabase keys from environment
- **Debug Mode**: Configurable via environment
- **Allowed Hosts**: Configurable host restrictions

## Error Handling

### API Error Responses
Standard HTTP status codes with descriptive error messages:

```python
# 400 Bad Request
{
  "error": "Message is required"
}

# 404 Not Found
{
  "error": "Lead not found"
}

# 500 Internal Server Error
{
  "error": "Failed to process message",
  "details": "OpenAI API unavailable"
}
```

### Database Error Handling
- **Connection Failures**: Graceful degradation with empty responses
- **Query Errors**: Logged errors with user-friendly messages
- **Credential Issues**: Startup warnings and fallback behavior

### AI Service Error Handling
- **OpenAI API Errors**: Rate limiting, quota exceeded, service unavailable
- **Function Call Errors**: Invalid parameters, execution failures
- **Context Errors**: Session corruption, memory issues

## Development Patterns

### Code Organization
- **Service Layer**: Business logic separated from views
- **Dependency Injection**: Services injected into views
- **Error Boundaries**: Consistent error handling across layers
- **Logging**: Comprehensive logging for debugging

### API Design Principles
- **RESTful Routes**: Standard HTTP methods and status codes
- **Consistent Responses**: Uniform JSON response structure
- **Validation**: Input validation at API boundaries
- **Documentation**: Clear endpoint documentation

### Async Processing Patterns
- **Task Queuing**: Background processing for long operations
- **Status Polling**: Frontend polling for task completion
- **Error Recovery**: Failed task handling and retry logic
- **Progress Updates**: Real-time status updates

## Configuration Management

### Environment Variables
Required environment variables in `.env` file:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# AI Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Django Settings Structure
- **Base Settings**: Core Django configuration
- **Database Settings**: Supabase connection configuration
- **API Settings**: DRF and CORS configuration
- **Third-party Settings**: OpenAI, Celery, Redis configuration

## Deployment

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations (if using Django models)
python manage.py migrate

# Start development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A backend worker --loglevel=info
```

### Production Considerations
- **WSGI/ASGI**: Production server configuration
- **Static Files**: Static file serving configuration
- **Database**: Production database settings
- **Redis**: Production Redis configuration
- **Environment**: Production environment variables
- **Logging**: Production logging configuration

### Docker Support
Potential Docker configuration for containerized deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Testing Strategy

### Test Structure
- **Unit Tests**: Individual function and method testing
- **Integration Tests**: API endpoint testing
- **Service Tests**: Database and external service testing
- **Mock Testing**: OpenAI and Supabase service mocking

### Test Examples
```python
# API endpoint testing
def test_leads_list_get(self):
    response = self.client.get('/leads/')
    self.assertEqual(response.status_code, 200)

# Service layer testing
def test_supabase_service_create_lead(self):
    lead_data = {'name': 'Test Lead', 'email': 'test@example.com'}
    result = SupabaseService.create_lead(lead_data)
    self.assertIsNotNone(result)
```

### Testing Commands
```bash
# Run all tests
python manage.py test

# Run specific test file
python manage.py test backend.api.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Performance Considerations

### Database Optimization
- **Query Optimization**: Efficient Supabase queries
- **Connection Pooling**: Database connection management
- **Indexing**: Proper database indexing for performance
- **Caching**: Redis caching for frequently accessed data

### API Performance
- **Response Compression**: Gzip compression for API responses
- **Pagination**: Large dataset pagination
- **Rate Limiting**: API rate limiting for protection
- **Async Processing**: Background tasks for heavy operations

### Memory Management
- **Session Cleanup**: Regular session cleanup
- **Context Limits**: Conversation context size limits
- **Task Cleanup**: Celery result cleanup
- **Connection Limits**: Database connection limits

## Monitoring & Logging

### Application Logging
```python
import logging

logger = logging.getLogger(__name__)

# Error logging
logger.error(f"Failed to create lead: {e}")

# Info logging
logger.info(f"Lead {lead_id} updated successfully")

# Debug logging
logger.debug(f"Processing message: {message}")
```

### Health Checks
- **Database Health**: Supabase connection status
- **Redis Health**: Celery broker connectivity
- **OpenAI Health**: API service availability
- **Task Queue Health**: Celery worker status

### Metrics Collection
- **API Metrics**: Request/response times, error rates
- **Database Metrics**: Query performance, connection counts
- **Task Metrics**: Task completion times, failure rates
- **AI Metrics**: OpenAI API usage, token consumption

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check Supabase credentials
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python manage.py shell
>>> from backend.api.supabase_client import get_supabase_client
>>> client = get_supabase_client()
```

**2. OpenAI API Errors**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API access
python -c "from openai import OpenAI; client = OpenAI(); print('API key valid')"
```

**3. Celery Task Issues**
```bash
# Check Redis connection
redis-cli ping

# Monitor Celery tasks
celery -A backend events

# Inspect task status
celery -A backend inspect active
```

**4. CORS Issues**
- Verify CORS_ALLOWED_ORIGINS includes frontend URL
- Check CORS_ALLOW_CREDENTIALS setting
- Ensure frontend sends credentials with requests

### Debug Tools
- **Django Debug Toolbar**: Development debugging
- **Django Shell**: Interactive debugging
- **Celery Flower**: Task monitoring web interface
- **Redis CLI**: Redis debugging and monitoring

## API Usage Examples

### Creating a Lead
```python
import requests

url = "http://localhost:8000/leads/"
data = {
    "name": "Jane Doe",
    "company": "Example Corp",
    "email": "jane@example.com",
    "phone": "+1-555-0199",
    "value": 75000,
    "status": "Interest",
    "source": "Website"
}

response = requests.post(url, json=data)
print(response.json())
```

### Chat Interaction
```python
import requests
import time

# Send message
chat_url = "http://localhost:8000/chat/"
message_data = {"message": "Move Jane Doe to meeting booked"}

response = requests.post(chat_url, json=message_data)
task_id = response.json()["task_id"]

# Poll for completion
status_url = f"http://localhost:8000/chat/status/{task_id}/"
while True:
    status_response = requests.get(status_url)
    status_data = status_response.json()
    
    if status_data["state"] == "SUCCESS":
        print(status_data["result"]["ai_message"])
        break
    elif status_data["state"] == "FAILURE":
        print("Error:", status_data["error"])
        break
    
    time.sleep(2)
```

## Future Enhancements

### Potential Improvements
1. **Authentication**: User authentication and authorization
2. **Permissions**: Role-based access control
3. **Webhooks**: Real-time notifications for lead changes
4. **Bulk Operations**: Batch lead operations
5. **Advanced Search**: Full-text search capabilities
6. **Analytics**: Lead pipeline analytics and reporting
7. **Email Integration**: Automated email workflows
8. **File Uploads**: Document attachment support

### Architectural Considerations
- **Microservices**: Service decomposition for scalability
- **Event Sourcing**: Event-driven architecture patterns
- **GraphQL**: Alternative API query language
- **WebSockets**: Real-time bidirectional communication
- **Caching Layer**: Advanced caching strategies
- **Message Queues**: Enhanced async processing

## Contributing Guidelines

### Code Style
- **PEP 8**: Python style guide compliance
- **Type Hints**: Function and method type annotations
- **Docstrings**: Comprehensive documentation strings
- **Comments**: Clear explanatory comments

### Development Workflow
1. **Feature Branch**: Create feature branch from main
2. **Environment**: Set up local development environment
3. **Testing**: Write tests for new functionality
4. **Documentation**: Update relevant documentation
5. **Code Review**: Submit pull request for review
6. **Integration**: Merge to main after approval

### Pull Request Process
- **Description**: Clear description of changes
- **Testing**: All tests passing
- **Coverage**: Maintain or improve test coverage
- **Documentation**: Updated documentation
- **Breaking Changes**: Clear migration path

This documentation provides a comprehensive overview of the backend architecture and should enable developers and AI assistants to effectively work with and extend the CRM API system.