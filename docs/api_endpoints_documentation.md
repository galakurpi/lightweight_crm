# API Endpoints Documentation - Lightweight CRM

## Overview

The backend API is built with Django 4.2.23 and Django REST Framework, providing a comprehensive RESTful API for the CRM system. The API handles lead management, AI-powered chat assistance, and asynchronous task processing.

## Architecture

### Tech Stack
- **Django**: 4.2.23 - Web framework and ORM
- **Django REST Framework**: RESTful API development
- **Supabase**: PostgreSQL database with real-time capabilities
- **OpenAI**: GPT-4 integration for AI chat assistant
- **Celery**: Asynchronous task processing
- **Redis**: Message broker for Celery tasks

### API Structure
```
Backend API Structure:
├── Base URL: http://localhost:8000/
├── Lead Management Endpoints
│   ├── GET/POST /leads/                    # List/create leads
│   ├── GET/PUT/DELETE /leads/{id}/         # Individual lead operations
│   └── PUT /leads/{id}/status/             # Update lead status (Kanban)
├── AI Chat Endpoints
│   ├── POST /chat/                         # Send message (async)
│   ├── GET /chat/status/{task_id}/         # Poll task status
│   └── POST /chat/clear/                   # Clear conversation
└── Utility Endpoints
    ├── GET /test/                          # API health check
    └── GET /admin/                         # Django admin interface
```

## Authentication & Security

- **Django Sessions**: Used for chat conversation context
- **CSRF Protection**: Built-in Django CSRF middleware
- **CORS Configuration**: Configured for React frontend (localhost:3000)

## Core API Endpoints

### Lead Management API

#### 1. List/Create Leads - `GET/POST /leads/`

**GET Request - List All Leads**
Returns all leads organized by status for Kanban board display.

**Response Structure:**
```json
{
  "Interest": [
    {
      "id": "uuid",
      "name": "John Doe",
      "company": "Acme Corp",
      "email": "john@acme.com",
      "phone": "+1234567890",
      "value": 5000.00,
      "notes": "Interested in premium package",
      "source": "Website",
      "status": "Interest",
      "card_order": 1,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "Meeting booked": [],
  "Proposal sent": [],
  "Closed win": [],
  "Closed lost": []
}
```

**POST Request - Create New Lead**
```json
{
  "name": "Jane Smith",           // Required
  "company": "Tech Solutions",    // Optional
  "email": "jane@tech.com",      // Optional
  "phone": "+1987654321",        // Optional
  "value": 7500.00,              // Optional
  "notes": "Follow up next week", // Optional
  "source": "Referral",          // Optional
  "status": "Interest"           // Optional (defaults to "Interest")
}
```

#### 2. Individual Lead Operations - `GET/PUT/DELETE /leads/{lead_id}/`

- **GET**: Retrieve specific lead details
- **PUT**: Update lead information (partial updates supported)
- **DELETE**: Permanently delete lead (returns 204 No Content)

#### 3. Update Lead Status - `PUT /leads/{lead_id}/status/`

For Kanban drag-and-drop operations:
```json
{
  "status": "Meeting booked",     // Required: new status
  "card_order": 3                // Optional: position in new column
}
```

**Valid Status Values:**
- `"Interest"`, `"Meeting booked"`, `"Proposal sent"`, `"Closed win"`, `"Closed lost"`

### AI Chat Assistant API

#### 1. Send Chat Message - `POST /chat/`

Initiates asynchronous AI message processing:
```json
{
  "message": "Show me all leads from Acme Corp"
}
```

**Response:**
```json
{
  "task_id": "celery-task-uuid",
  "status": "processing",
  "message": "Message received, processing..."
}
```

#### 2. Poll Task Status - `GET /chat/status/{task_id}/`

Poll for asynchronous task completion. Frontend polls every 2 seconds until completion.

**Response States:**
- **PENDING**: `{"state": "PENDING", "status": "Task is waiting..."}`
- **PROCESSING**: `{"state": "PROCESSING", "status": "Processing your message..."}`
- **SUCCESS**: 
```json
{
  "state": "SUCCESS",
  "result": {
    "message": "I found 2 leads from Acme Corp...",
    "leads_data": [...],
    "actions_performed": []
  }
}
```
- **FAILURE**: `{"state": "FAILURE", "error": "Error details", "status": "Task failed"}`

#### 3. Clear Conversation - `POST /chat/clear/`

Resets AI conversation context and memory.

### Utility Endpoints

- **GET /test/**: API health check - Returns `{"message": "Django API is working!", "status": "success"}`

## AI Chat Functionality

### OpenAI Integration
Uses GPT-4 Turbo with function calling capabilities:

**Available AI Functions:**
1. **search_leads**: Find leads by name, company, or email
2. **update_lead_status**: Change lead pipeline status
3. **update_lead_data**: Modify specific lead fields
4. **create_lead**: Add new leads via conversation
5. **delete_lead**: Remove leads (with confirmation)

**Example AI Interactions:**
- "Show me all leads from Microsoft"
- "Move John Doe to meeting booked status"
- "Create a new lead for Sarah Johnson at Google"

### Conversation Context Management
- **Session Storage**: History stored in Django sessions
- **Context Limit**: Maintains last 10 messages for performance
- **Session Duration**: 24-hour session timeout

## Asynchronous Processing

### Celery Task System
- **Broker**: Redis (localhost:6379)
- **Timeout**: 30 minutes per task
- **Task States**: PENDING → PROCESSING → SUCCESS/FAILURE

## Data Models

### Lead Data Structure
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

**Source Options:** Website, Referral, Social Media, Cold Call, Email Campaign, Trade Show, Other

## Database Integration

### Supabase Configuration
- **Connection**: Via SUPABASE_URL and SUPABASE_KEY environment variables
- **Table**: `leads` table with UUID primary keys
- **Operations**: get_all_leads(), create_lead(), update_lead(), delete_lead(), get_lead_by_id()

## Environment Configuration

### Required Environment Variables
```bash
# Django Configuration
SECRET_KEY=your-django-secret-key
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

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful GET/PUT requests
- **201 Created**: Successful POST requests
- **204 No Content**: Successful DELETE requests
- **400 Bad Request**: Invalid request data
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

### Error Response Format
```json
{
  "error": "Human-readable error message",
  "details": "Technical error details (optional)"
}
```

## API Usage Examples

### Frontend Integration Patterns
```javascript
// Fetching leads for Kanban board
const fetchLeads = async () => {
  const response = await fetch('/leads/');
  return response.json();
};

// Creating new lead
const createLead = async (leadData) => {
  const response = await fetch('/leads/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(leadData)
  });
  return response.json();
};

// AI chat with polling
const sendChatMessage = async (message) => {
  const response = await fetch('/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  const { task_id } = await response.json();
  
  // Poll for result
  const pollResult = async () => {
    const statusResponse = await fetch(`/chat/status/${task_id}/`);
    const status = await statusResponse.json();
    
    if (status.state === 'SUCCESS') {
      return status.result;
    } else if (status.state === 'FAILURE') {
      throw new Error(status.error);
    } else {
      setTimeout(pollResult, 2000);
    }
  };
  
  return pollResult();
};
```

## Development Workflow

### Local Development Setup
```bash
# Backend setup
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A backend worker --loglevel=info

# Start Redis server
redis-server
```

### API Testing
```bash
# Test API health
curl http://localhost:8000/test/

# Get all leads
curl http://localhost:8000/leads/

# Create new lead
curl -X POST http://localhost:8000/leads/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Lead", "company": "Test Corp"}'
```

## Security Best Practices

- **Input Validation**: All inputs validated before database operations
- **CORS Configuration**: Restricted to specific frontend origins
- **Environment Security**: All secrets via environment variables
- **API Key Protection**: OpenAI and Supabase keys secured

## Future Enhancements

### Potential API Improvements
1. **Authentication**: JWT or OAuth2 implementation
2. **Rate Limiting**: API throttling for production use
3. **Pagination**: Large dataset handling
4. **Filtering**: Query parameters for lead filtering
5. **Webhooks**: Real-time notifications
6. **Batch Operations**: Bulk lead operations
7. **File Uploads**: Attachment support
8. **Audit Logging**: Change tracking

This comprehensive API documentation provides all necessary information to effectively work with and extend the CRM backend system.