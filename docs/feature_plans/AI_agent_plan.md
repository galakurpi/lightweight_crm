# AI Chat Widget Implementation Plan

## Changes Overview
We will implement a comprehensive AI-powered chat widget that integrates with the existing CRM system. The solution includes a minimalist floating chat interface on the frontend, a Django backend with OpenAI function calling integration, session-based conversation memory, and intelligent lead matching. The AI agent will handle intent routing, lead identification, and CRUD operations on leads through natural language commands with structured confirmations.

## User Flow
1. **Initial State**: User sees a small floating chat button in bottom-right corner of the CRM interface
2. **Chat Activation**: User clicks the floating button, expanding into a minimalist chat interface (300x400px)
3. **Conversation**: User types natural language commands about leads ("Move John to Meeting booked", "Add new lead Sarah from TechCorp")
4. **AI Processing**: System processes message through intent routing → lead finding → action execution pipeline
5. **Confirmation**: AI provides structured confirmation of actions taken ("Lead 'John Smith' status updated to 'Meeting booked'")
6. **Context Retention**: Conversation context maintained across messages until user clicks clear button
7. **Session Management**: Context stored in Django sessions, cleared on demand. We don't store conversation history, only the current conversation.

## Tech Stack & APIs
- **Frontend**: React with existing structure, CSS for chat widget styling
- **Backend**: Django REST Framework with new chat endpoints
- **AI Service**: OpenAI GPT-4.1 with function calling API
- **Session Storage**: Django's built-in session framework
- **Database**: Existing Supabase integration for lead operations
- **HTTP Client**: Existing httpx for OpenAI API calls
- **Async Processing**: Celery with Redis/Database broker for background AI processing

## Core Features
1. **Floating Chat Widget**: Minimalist expandable interface in bottom-right corner
2. **Natural Language Processing**: Intent routing for lead operations (create, update, delete, query, status change)
3. **Context-Aware Lead Matching**: Smart lead identification using conversation context and fuzzy matching
4. **Session-Based Memory**: Conversation persistence with manual clear functionality
5. **Structured Confirmations**: Formal, brief responses confirming actions taken
6. **Error Handling**: Specific handling for common errors (lead not found, database unavailable, ambiguous input)
7. **Function Calling Integration**: OpenAI structured functions for reliable lead operations
8. **Asynchronous Processing**: Background task handling for AI responses with real-time status updates

## Implementation Steps

### Backend Implementation

#### 1. Install Dependencies
- Add `openai==1.12.0` to requirements.txt
- Add `celery==5.3.4` to requirements.txt
- Add `redis==5.0.1` to requirements.txt (or use Django database broker)

#### 2. Setup Async Task Processing
- Configure Celery in `backend/celery.py`
- Add Celery configuration to `backend/settings.py`
- Create `backend/api/tasks.py` for background AI processing

#### 3. Create Chat Service Module //TODO : USE AGENT TO MATCH
- Create `backend/api/chat_service.py` with OpenAI client initialization
- Implement conversation context management functions
- Create intent routing and lead matching logic

#### 4. Define OpenAI Function Schemas
- Create structured function definitions for lead operations
- Implement lead search, create, update, delete, and status change functions
- Add error handling for each function

#### 5. Create Chat API Endpoints
- Add `chat/` endpoint in `backend/api/urls.py` (initiates async task)
- Add `chat/status/<task_id>/` endpoint for checking task status
- Add `chat/clear/` endpoint for clearing conversation context
- Implement session-based context storage and retrieval

#### 6. Implement Chat Views
- Create `chat_message` view for initiating async AI processing
- Create `chat_status` view for polling task status and results
- Create `clear_chat` view for clearing conversation context
- Add comprehensive error handling with specific error types

#### 7. Add Environment Configuration
- Add OpenAI API key configuration to Django settings
- Add Celery/Redis configuration to Django settings
- Update settings.py to handle OpenAI and async processing credentials //TODO: CHECK IF REDIS/CELERY CREDENTIALS ARE FINE


### Frontend Implementation

#### 8. Create Chat Widget Components
- Create `frontend/src/components/ChatWidget.js` - main chat interface
- Create `frontend/src/components/ChatButton.js` - floating button
- Create `frontend/src/components/ChatMessage.js` - individual message component

#### 9. Implement Chat Widget Styling
- Create `frontend/src/components/ChatWidget.css` with minimalist design
- Add responsive positioning for bottom-right corner
- Implement smooth expand/collapse animations
- Add loading/typing indicators for async processing

#### 10. Add Chat Widget State Management
- Implement React state for chat messages and widget visibility
- Add API integration for sending messages and polling for responses
- Handle loading states, typing indicators, and error display
- Implement polling mechanism for checking task status

#### 11. Integrate Chat Widget into Main App
- Import and add ChatWidget component to `frontend/src/App.js`
- Ensure chat widget appears on all pages
- Test integration with existing CRM functionality

### Testing and Refinement

#### 12. Test Core Functionality
- Test intent routing for all lead operations
- Verify lead matching with various input formats
- Confirm session-based context retention
- Test async processing and polling mechanism

#### 13. Test Error Scenarios
- Test lead not found scenarios
- Test database connection errors
- Test ambiguous input handling
- Test async task failures and timeouts

#### 14. UI/UX Testing
- Test chat widget positioning and responsiveness
- Verify smooth animations and transitions
- Test loading indicators and typing states
- Test on different screen sizes

#### 15. Integration Testing
- Test chat widget with existing Kanban board functionality
- Verify lead updates reflect in real-time on the board
- Test session persistence across page refreshes

## Implementation Checklist

### Backend Tasks
- [ ] Add `openai==1.12.0` to requirements.txt
- [ ] Add `celery==5.3.4` to requirements.txt
- [ ] Add `redis==5.0.1` to requirements.txt
- [ ] Configure Celery in `backend/celery.py`
- [ ] Add Celery configuration to `backend/settings.py`
- [ ] Create `backend/api/tasks.py` for background AI processing
- [ ] Create `backend/api/chat_service.py` with OpenAI client setup
- [ ] Add OpenAI API key configuration to `backend/settings.py`
- [ ] Create OpenAI function schemas for lead operations in chat_service.py
- [ ] Implement conversation context management functions in chat_service.py
- [ ] Add chat endpoints to `backend/api/urls.py` (including status polling)
- [ ] Create `chat_message` view in `backend/api/views.py` (async task initiation)
- [ ] Create `chat_status` view in `backend/api/views.py` (task status polling)
- [ ] Create `clear_chat` view in `backend/api/views.py`
- [ ] Implement session-based context storage in chat views
- [ ] Add comprehensive error handling for common scenarios

### Frontend Tasks
- [ ] Create `frontend/src/components/ChatButton.js` component
- [ ] Create `frontend/src/components/ChatWidget.js` component
- [ ] Create `frontend/src/components/ChatMessage.js` component
- [ ] Create `frontend/src/components/ChatWidget.css` with minimalist styling and loading indicators
- [ ] Implement chat widget state management in ChatWidget.js
- [ ] Add API integration functions for chat messages and status polling
- [ ] Implement polling mechanism for async task status
- [ ] Add loading states and typing indicators
- [ ] Integrate ChatWidget component into `frontend/src/App.js`

### Testing Tasks
- [ ] Test intent routing for status updates
- [ ] Test intent routing for lead data updates
- [ ] Test intent routing for lead creation
- [ ] Test intent routing for lead deletion
- [ ] Test lead matching with partial names
- [ ] Test lead matching with company names
- [ ] Test conversation context retention
- [ ] Test clear conversation functionality
- [ ] Test async processing and task polling
- [ ] Test loading indicators and typing states
- [ ] Test error handling for lead not found
- [ ] Test error handling for database unavailable
- [ ] Test error handling for ambiguous input
- [ ] Test error handling for async task failures
- [ ] Test chat widget positioning and animations
- [ ] Test integration with existing Kanban board updates

## File Structure
```
backend/
├── api/
│   ├── chat_service.py          # New - OpenAI integration & chat logic
│   ├── tasks.py                 # New - Celery background tasks
│   ├── views.py                 # Modified - Add chat endpoints
│   └── urls.py                  # Modified - Add chat routes
├── celery.py                    # New - Celery configuration
├── settings.py                  # Modified - Add OpenAI & Celery config
└── requirements.txt             # Modified - Add openai, celery, redis

frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.js        # New - Main chat interface with polling
│   │   ├── ChatWidget.css       # New - Chat styling with loading states
│   │   ├── ChatButton.js        # New - Floating button
│   │   └── ChatMessage.js       # New - Message component
│   └── App.js                   # Modified - Integrate chat widget
```

## API Endpoints
- `POST /chat/` - Initiate async chat message processing, returns task_id
- `GET /chat/status/<task_id>/` - Poll for task status and results
- `POST /chat/clear/` - Clear conversation context from session

## Async Processing Flow
1. **User sends message** → Frontend calls `POST /chat/` with message
2. **Backend initiates task** → Returns `task_id` immediately
3. **Frontend polls status** → Calls `GET /chat/status/<task_id>/` every 1-2 seconds
4. **Task completes** → Returns AI response and lead operation results
5. **Frontend updates UI** → Shows response and refreshes lead data if needed