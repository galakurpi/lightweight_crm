# API Endpoints Documentation - Lightweight CRM

## Overview

The backend API is built with Django 4.2.23 and Django REST Framework, providing a comprehensive RESTful API for the CRM system. The API handles lead management, AI-powered chat assistance, and asynchronous task processing. All endpoints return JSON responses and follow REST conventions with proper HTTP status codes.

## Architecture

### Tech Stack
- **Django**: 4.2.23 - Web framework and ORM
- **Django REST Framework**: RESTful API development
- **Supabase**: PostgreSQL database with real-time capabilities
- **OpenAI**: GPT-4 integration for AI chat assistant
- **Celery**: Asynchronous task processing
- **Redis**: Message broker for Celery tasks
- **CORS Headers**: Cross-origin resource sharing for React frontend

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

### Session-Based Authentication
- **Django Sessions**: Used for chat conversation context
- **CSRF Protection**: Built-in Django CSRF middleware
- **CORS Configuration**: Configured for React frontend (localhost:3000)

### Security Headers
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
]
CORS_ALLOW_CREDENTIALS = True
```

## Core API Endpoints

### Lead Management API

#### 1. List/Create Leads
**Endpoint:** `GET/POST /leads/`

**GET Request - List All Leads**
- **Purpose**: Retrieve all leads organized by status for Kanban board display
- **Method**: `GET`
- **Authentication**: None required
- **Response Format**: JSON object with status-grouped leads

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
- **Purpose**: Create a new lead with automatic status and ordering
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Authentication**: None required

**Request Body:**
```json
{
  "name": "Jane Smith",           // Required
  "company": "Tech Solutions",    // Optional
  "email": "jane@tech.com",      // Optional
  "phone": "+1987654321",        // Optional
  "value": 7500.00,              // Optional (numeric)
  "notes": "Follow up next week", // Optional
  "source": "Referral",          // Optional
  "status": "Interest"           // Optional (defaults to "Interest")
}
```

**Response (201 Created):**
```json
{
  "id": "new-uuid",
  "name": "Jane Smith",
  "company": "Tech Solutions",
  "email": "jane@tech.com",
  "phone": "+1987654321",
  "value": 7500.00,
  "notes": "Follow up next week",
  "source": "Referral",
  "status": "Interest",
  "card_order": 2,
  "created_at": "2024-01-15T11:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid data or missing required fields
```json
{
  "error": "Failed to create lead"
}
```

#### 2. Individual Lead Operations
**Endpoint:** `GET/PUT/DELETE /leads/{lead_id}/`

**GET Request - Retrieve Lead Details**
- **Purpose**: Get detailed information for a specific lead
- **Method**: `GET`
- **URL Parameter**: `lead_id` (string, UUID)

**Response (200 OK):**
```json
{
  "id": "lead-uuid",
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
```

**Error Response (404 Not Found):**
```json
{
  "error": "Lead not found"
}
```

**PUT Request - Update Lead**
- **Purpose**: Update lead information (partial updates supported)
- **Method**: `PUT`
- **Content-Type**: `application/json`

**Request Body (partial update example):**
```json
{
  "company": "Updated Company Name",
  "value": 8000.00,
  "notes": "Updated notes with new information"
}
```

**Response (200 OK):**
```json
{
  "id": "lead-uuid",
  "name": "John Doe",
  "company": "Updated Company Name",
  "email": "john@acme.com",
  "phone": "+1234567890",
  "value": 8000.00,
  "notes": "Updated notes with new information",
  "source": "Website",
  "status": "Interest",
  "card_order": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**DELETE Request - Remove Lead**
- **Purpose**: Permanently delete a lead from the system
- **Method**: `DELETE`

**Response (204 No Content):**
- Empty response body on successful deletion

**Error Responses:**
- `400 Bad Request`: Failed to update/delete lead
- `404 Not Found`: Lead doesn't exist

#### 3. Update Lead Status (Kanban Operations)
**Endpoint:** `PUT /leads/{lead_id}/status/`

- **Purpose**: Update lead status and card order for Kanban drag-and-drop
- **Method**: `PUT`
- **Content-Type**: `application/json`
- **Use Case**: Moving cards between Kanban columns

**Request Body:**
```json
{
  "status": "Meeting booked",     // Required: new status
  "card_order": 3                // Optional: position in new column
}
```

**Valid Status Values:**
- `"Interest"`
- `"Meeting booked"`
- `"Proposal sent"`
- `"Closed win"`
- `"Closed lost"`

**Response (200 OK):**
```json
{
  "id": "lead-uuid",
  "name": "John Doe",
  "company": "Acme Corp",
  "email": "john@acme.com",
  "phone": "+1234567890",
  "value": 5000.00,
  "notes": "Meeting scheduled for next week",
  "source": "Website",
  "status": "Meeting booked",
  "card_order": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Missing or invalid status
```json
{
  "error": "Status is required"
}
```

### AI Chat Assistant API

#### 1. Send Chat Message (Async Processing)
**Endpoint:** `POST /chat/`

- **Purpose**: Initiate asynchronous AI message processing
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Processing**: Returns immediately with task ID for polling
- **Session**: Uses Django sessions for conversation context

**Request Body:**
```json
{
  "message": "Show me all leads from Acme Corp"
}
```

**Response (200 OK):**
```json
{
  "task_id": "celery-task-uuid",
  "status": "processing",
  "message": "Message received, processing..."
}
```

**Error Responses:**
- `400 Bad Request`: Missing message
```json
{
  "error": "Message is required"
}
```
- `500 Internal Server Error`: Processing failure
```json
{
  "error": "Failed to process message",
  "details": "Specific error details"
}
```

#### 2. Poll Task Status
**Endpoint:** `GET /chat/status/{task_id}/`

- **Purpose**: Poll for asynchronous task completion and results
- **Method**: `GET`
- **URL Parameter**: `task_id` (string, Celery task UUID)
- **Polling**: Frontend polls every 2 seconds until completion

**Response States:**

**PENDING State:**
```json
{
  "state": "PENDING",
  "status": "Task is waiting to be processed..."
}
```

**PROCESSING State:**
```json
{
  "state": "PROCESSING",
  "status": "Processing your message..."
}
```

**SUCCESS State:**
```json
{
  "state": "SUCCESS",
  "result": {
    "message": "I found 2 leads from Acme Corp:\n\n1. John Doe - Status: Interest\n2. Jane Smith - Status: Meeting booked",
    "leads_data": [
      {
        "id": "lead-1-uuid",
        "name": "John Doe",
        "company": "Acme Corp",
        "status": "Interest"
      },
      {
        "id": "lead-2-uuid", 
        "name": "Jane Smith",
        "company": "Acme Corp",
        "status": "Meeting booked"
      }
    ],
    "actions_performed": []
  }
}
```

**FAILURE State:**
```json
{
  "state": "FAILURE",
  "error": "OpenAI API error: Rate limit exceeded",
  "status": "Task failed"
}
```

#### 3. Clear Conversation Context
**Endpoint:** `POST /chat/clear/`

- **Purpose**: Reset AI conversation context and memory
- **Method**: `POST`
- **Authentication**: Uses Django session

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Conversation context cleared"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Failed to clear conversation",
  "details": "Session error details"
}
```

### Utility Endpoints

#### API Health Check
**Endpoint:** `GET /test/`

- **Purpose**: Verify API functionality and connectivity
- **Method**: `GET`
- **Authentication**: None required

**Response (200 OK):**
```json
{
  "message": "Django API is working!",
  "status": "success"
}
```

## AI Chat Functionality

### OpenAI Integration
The chat system uses GPT-4 Turbo with function calling capabilities to perform CRM operations:

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
- "Update the phone number for lead ID abc-123"

### Conversation Context Management
- **Session Storage**: Conversation history stored in Django sessions
- **Context Limit**: Maintains last 10 messages for performance
- **Session Duration**: 24-hour session timeout
- **Memory**: AI remembers context within conversation session

## Asynchronous Processing

### Celery Task System
**Configuration:**
- **Broker**: Redis (localhost:6379)
- **Backend**: Redis result storage
- **Serialization**: JSON format
- **Timeout**: 30 minutes per task
- **Monitoring**: Task state tracking enabled

**Task Flow:**
1. User sends message → POST /chat/ returns task_id
2. Celery worker processes message with OpenAI
3. Frontend polls GET /chat/status/{task_id}/ every 2 seconds
4. Task completes → Result returned to frontend
5. UI updates with AI response

**Task States:**
- `PENDING`: Task queued, waiting for worker
- `PROCESSING`: Worker actively processing
- `SUCCESS`: Task completed successfully
- `FAILURE`: Task failed with error details

## Data Models

### Lead Data Structure
```python
Lead = {
    "id": str,              # UUID primary key
    "name": str,            # Contact name (required)
    "company": str,         # Company name (optional)
    "email": str,           # Email address (optional)
    "phone": str,           # Phone number (optional)
    "value": float,         # Deal value in dollars (optional)
    "notes": str,           # Additional notes (optional)
    "source": str,          # Lead source (optional)
    "status": str,          # Pipeline status (required)
    "card_order": int,      # Position in Kanban column
    "created_at": datetime, # Creation timestamp
    "updated_at": datetime  # Last modification timestamp
}
```

**Status Values:**
- `"Interest"` - Initial lead stage
- `"Meeting booked"` - Meeting scheduled
- `"Proposal sent"` - Proposal delivered
- `"Closed win"` - Deal won
- `"Closed lost"` - Deal lost

**Source Options:**
- Website, Referral, Social Media, Cold Call, Email Campaign, Trade Show, Other

## Database Integration

### Supabase Configuration
**Connection:**
- **URL**: Configured via SUPABASE_URL environment variable
- **API Key**: Configured via SUPABASE_KEY environment variable
- **Table**: `leads` table with UUID primary keys
- **Real-time**: Supabase real-time capabilities available (not currently used)

**Database Operations:**
- `get_all_leads()` - Fetch all leads with ordering
- `create_lead()` - Insert new lead record
- `update_lead()` - Update existing lead
- `delete_lead()` - Remove lead record
- `get_lead_by_id()` - Fetch specific lead

**Error Handling:**
- Connection failures gracefully handled
- Database errors logged and returned as HTTP errors
- Placeholder data returned when Supabase unavailable

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

### Development vs Production
**Development Settings:**
- DEBUG=True
- SQLite fallback database
- Local Redis instance
- CORS enabled for localhost:3000

**Production Considerations:**
- DEBUG=False
- PostgreSQL database (via Supabase)
- Redis cluster for high availability
- Proper CORS configuration
- Environment-specific allowed hosts

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful GET/PUT requests
- **201 Created**: Successful POST requests (lead creation)
- **204 No Content**: Successful DELETE requests
- **400 Bad Request**: Invalid request data or missing required fields
- **404 Not Found**: Resource not found (lead doesn't exist)
- **500 Internal Server Error**: Server-side errors (database, OpenAI, etc.)

### Error Response Format
```json
{
  "error": "Human-readable error message",
  "details": "Technical error details (optional)"
}
```

### Common Error Scenarios
1. **Missing Required Fields**: 400 with validation errors
2. **Lead Not Found**: 404 with "Lead not found" message
3. **Database Connection Issues**: 500 with connection error details
4. **OpenAI API Errors**: 500 with API error message
5. **Celery Task Failures**: Task state FAILURE with error details

## API Usage Examples

### Frontend Integration Patterns
**Fetching Leads for Kanban Board:**
```javascript
const fetchLeads = async () => {
  const response = await fetch('/leads/');
  const kanbanData = await response.json();
  return kanbanData;
};
```

**Creating New Lead:**
```javascript
const createLead = async (leadData) => {
  const response = await fetch('/leads/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(leadData)
  });
  return response.json();
};
```

**Kanban Drag & Drop:**
```javascript
const updateLeadStatus = async (leadId, newStatus, cardOrder) => {
  const response = await fetch(`/leads/${leadId}/status/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status: newStatus, card_order: cardOrder })
  });
  return response.json();
};
```

**AI Chat with Polling:**
```javascript
const sendChatMessage = async (message) => {
  // Send message
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
      // Continue polling
      setTimeout(pollResult, 2000);
    }
  };
  
  return pollResult();
};
```

## Performance Considerations

### Database Optimization
- **Indexing**: Proper indexes on status and card_order fields
- **Query Optimization**: Efficient lead retrieval with ordering
- **Connection Pooling**: Supabase handles connection management

### Caching Strategy
- **Session Caching**: Conversation context cached in Django sessions
- **Lead Data**: No caching currently implemented (real-time data priority)
- **Static Assets**: Django static files handling

### Scalability
- **Horizontal Scaling**: Stateless API design supports multiple instances
- **Database Scaling**: Supabase provides automatic scaling
- **Task Processing**: Celery workers can be scaled independently
- **Load Balancing**: API endpoints are stateless and load-balancer friendly

## Security Best Practices

### Data Protection
- **Input Validation**: All inputs validated before database operations
- **SQL Injection**: Supabase client handles parameterized queries
- **XSS Prevention**: JSON API responses prevent XSS attacks

### API Security
- **CORS Configuration**: Restricted to specific frontend origins
- **CSRF Protection**: Django CSRF middleware enabled
- **Rate Limiting**: Not currently implemented (consider for production)

### Environment Security
- **Secret Management**: All secrets via environment variables
- **API Key Protection**: OpenAI and Supabase keys secured
- **Debug Mode**: Disabled in production environments

## Testing Strategy

### API Testing
- **Unit Tests**: Individual endpoint testing
- **Integration Tests**: End-to-end API workflows
- **Mock Testing**: External service mocking (OpenAI, Supabase)

### Testing Tools
- **Django Test Framework**: Built-in testing capabilities
- **DRF Test Client**: API endpoint testing
- **Mock Libraries**: External service mocking

## Monitoring & Logging

### Application Logging
- **Django Logging**: Built-in logging framework
- **Error Tracking**: Console output for development
- **Task Monitoring**: Celery task state tracking

### Health Monitoring
- **API Health Check**: `/test/` endpoint for monitoring
- **Database Health**: Supabase connection status
- **Redis Health**: Celery broker connectivity

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

## Future Enhancements

### Potential API Improvements
1. **Authentication**: JWT or OAuth2 implementation
2. **Rate Limiting**: API throttling for production use
3. **Pagination**: Large dataset handling for leads endpoint
4. **Filtering**: Query parameters for lead filtering/searching
5. **Webhooks**: Real-time notifications for external systems
6. **API Versioning**: Version management for backward compatibility
7. **Batch Operations**: Bulk lead operations support
8. **File Uploads**: Attachment support for leads
9. **Audit Logging**: Change tracking and audit trails
10. **Real-time WebSockets**: Live updates without polling

### Integration Opportunities
- **CRM Integrations**: Salesforce, HubSpot API bridges
- **Email Integration**: Email sending and tracking
- **Calendar Integration**: Meeting scheduling automation
- **Analytics API**: Reporting and dashboard data endpoints
- **Export API**: Data export in various formats (CSV, PDF)

This comprehensive API documentation provides developers and AI assistants with all necessary information to effectively work with and extend the CRM backend system.