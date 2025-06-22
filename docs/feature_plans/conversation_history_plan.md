# Conversation History with User Authentication Implementation Plan

## Changes Overview
We will extend the existing AI chat widget with persistent conversation history functionality using Django's built-in authentication system. The implementation adds a user management system where each user has their own leads and conversation history, similar to ChatGPT's interface. A sidebar within the chat widget will display conversation history with lazy loading, and conversation titles will be generated from the first user message. The system will use a three-table database structure (users, conversations, messages) with Supabase integration.

## User Flow
1. **Authentication**: User visits CRM and sees login screen if not authenticated
2. **Login**: User enters email/password using Django's authentication system
3. **Dashboard Access**: After login, user sees their personalized CRM with their own leads
4. **Chat Activation**: User clicks floating chat button, widget expands showing conversation history sidebar
5. **Conversation Selection**: User can click on previous conversations from sidebar to continue them
6. **New Conversation**: User can start new conversation, which auto-saves with title from first message
7. **Conversation Persistence**: All messages are permanently stored and accessible across sessions
8. **Lead Operations**: AI continues to perform lead operations, but only on user's own leads
9. **Session Management**: User remains logged in until logout, all conversations persist

## Tech Stack & APIs
- **Authentication**: Django's built-in authentication system with email/password
- **Frontend**: React with existing structure, extended chat widget with sidebar
- **Backend**: Django REST Framework with extended chat endpoints and user management
- **Database**: Supabase with new tables (users, conversations, messages)
- **AI Service**: OpenAI GPT-4.1 with function calling API (existing)
- **Session Storage**: Django sessions for authentication state
- **Async Processing**: Existing Celery setup for background AI processing

## Core Features
1. **User Authentication**: Django login/logout system with email/password
2. **User-Specific Data**: Each user has their own leads and conversations
3. **Conversation History Sidebar**: ChatGPT-style sidebar within chat widget
4. **Persistent Conversations**: All messages stored permanently in database
5. **Auto-Generated Titles**: Conversation titles from first user message (truncated if long)
6. **Conversation Management**: Create, select, and continue conversations
7. **Lazy Loading**: Conversation list loads on demand, all messages load when conversation selected
8. **User Migration**: Existing leads assigned to default admin user

## Database Schema

### New Tables in Supabase:
```sql
-- Users table (extends Django's auth)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    function_results JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Update leads table to include user ownership
ALTER TABLE leads ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE CASCADE;
```

## Implementation Steps

### Database Schema Setup

#### 1. Create User Management
- Extend Django's User model or use built-in User model
- Create migration to add default admin user
- Update leads table to include user_id foreign key
- Migrate existing leads to default admin user

#### 2. Create Conversation Tables
- Create `conversations` table with (id, user_id, title, created_at, updated_at)
- Create `messages` table with (id, conversation_id, content, is_user, timestamp, function_results)
- Add Supabase table creation via Django management command or direct SQL

#### 3. Update Supabase Service
- Extend SupabaseService to handle user-specific lead queries
- Add conversation and message CRUD operations
- Update all lead operations to filter by current user

### Backend Authentication & API Updates

#### 4. Implement Authentication Views
- Create login view using Django's authentication
- Create logout view
- Add authentication middleware to protect chat endpoints
- Create user context middleware for current user access

#### 5. Update Chat Service for Users
- Modify ChatService to work with user-specific data
- Update conversation context to use database instead of sessions
- Add conversation creation and retrieval methods
- Update lead operations to filter by current user

#### 6. Create Conversation API Endpoints
- Add `GET /conversations/` endpoint to list user's conversations
- Add `POST /conversations/` endpoint to create new conversation
- Add `GET /conversations/<id>/messages/` endpoint to get conversation messages
- Add `PUT /conversations/<id>/` endpoint to update conversation title

#### 7. Update Existing Chat Endpoints
- Modify chat endpoints to require authentication
- Update chat processing to save messages to database
- Link chat messages to specific conversations
- Ensure all lead operations respect user ownership

### Frontend Authentication & UI Updates

#### 8. Create Authentication Components
- Create `Login.js` component with email/password form
- Create `AuthContext.js` for managing authentication state
- Add authentication check to main App component
- Create logout functionality in header

#### 9. Extend Chat Widget with Sidebar
- Modify `ChatWidget.js` to include conversation history sidebar
- Create `ConversationList.js` component for sidebar
- Create `ConversationItem.js` component for individual conversation entries
- Add conversation selection and switching functionality

#### 10. Update Chat Widget State Management
- Add conversation management to chat widget state
- Implement conversation creation when starting new chat
- Add message persistence to database instead of local state
- Handle conversation switching and message loading

#### 11. Style Conversation History Interface
- Extend `ChatWidget.css` with sidebar styling
- Add responsive design for conversation list
- Implement conversation selection highlighting
- Add new conversation button and styling

### Data Migration & Testing

#### 12. Create Data Migration Scripts
- Create Django management command to set up default admin user
- Create script to migrate existing leads to admin user
- Create Supabase table setup script
- Test migration with existing data

#### 13. Test Authentication Flow
- Test login/logout functionality
- Test user-specific data isolation
- Test conversation creation and persistence
- Test conversation history loading

#### 14. Test Chat Integration
- Test conversation switching within chat widget
- Test message persistence across sessions
- Test conversation title generation
- Test user-specific lead operations

#### 15. Integration Testing
- Test complete user flow from login to chat usage
- Test data isolation between different users
- Test conversation history with multiple conversations
- Test lead operations with user authentication

## IMPLEMENTATION CHECKLIST:

### Database & Migration Tasks
1. Create Django migration to add user_id to leads table
2. Create Django management command to create default admin user
3. Create Django management command to migrate existing leads to admin user
4. Create conversations table in Supabase with user_id foreign key
5. Create messages table in Supabase with conversation_id foreign key
6. Update SupabaseService to include user filtering for all lead operations
7. Add conversation CRUD methods to SupabaseService
8. Add message CRUD methods to SupabaseService

### Backend Authentication Tasks
9. Create login view in views.py using Django authentication
10. Create logout view in views.py
11. Add authentication required decorators to existing chat endpoints
12. Create middleware to inject current user into request context
13. Update ChatService to accept user parameter and filter operations
14. Modify conversation context methods to use database instead of sessions
15. Add conversation management methods to ChatService
16. Create GET /conversations/ endpoint to list user conversations
17. Create POST /conversations/ endpoint to create new conversation
18. Create GET /conversations/<id>/messages/ endpoint
19. Create PUT /conversations/<id>/ endpoint to update conversation title
20. Update chat_message view to save messages to database
21. Update chat_message view to create conversation if none exists
22. Add conversation_id parameter to chat processing
23. Update all chat endpoints to work with authenticated users only

### Frontend Authentication Tasks
24. Create Login.js component with email/password form
25. Create AuthContext.js for authentication state management
26. Wrap App.js with AuthContext provider
27. Add authentication check to App.js main component
28. Create logout button in Header.js component
29. Add login form styling to appropriate CSS file
30. Handle authentication errors and loading states

### Frontend Chat Widget Updates
31. Modify ChatWidget.js to include conversation history sidebar
32. Create ConversationList.js component for sidebar conversation list
33. Create ConversationItem.js component for individual conversation display
34. Add conversation selection state management to ChatWidget
35. Add new conversation creation functionality to ChatWidget
36. Update message loading to fetch from database via API
37. Add conversation switching functionality
38. Implement conversation title display and editing
39. Update ChatWidget.css to include sidebar styling
40. Add responsive design for conversation sidebar
41. Style conversation selection and highlighting
42. Add new conversation button styling
43. Update chat widget layout to accommodate sidebar

### API Integration Tasks
44. Create API service functions for conversation management
45. Update existing chat API calls to include authentication headers
46. Add conversation loading API integration
47. Add message loading API integration for selected conversations
48. Add conversation creation API integration
49. Add conversation title update API integration
50. Handle API authentication errors in frontend

### Testing Tasks
51. Test user login and logout functionality
52. Test conversation creation when starting new chat
53. Test conversation history loading and display
54. Test conversation switching functionality
55. Test message persistence across browser sessions
56. Test conversation title generation from first message
57. Test user data isolation (users only see their own data)
58. Test lead operations work only on user's own leads
59. Test authentication required for all chat endpoints
60. Test default admin user has access to existing leads
61. Test complete user flow from login to conversation management
62. Test responsive design of conversation sidebar
63. Test error handling for authentication failures
64. Test conversation loading performance

## API Endpoints

### Authentication Endpoints
- `POST /auth/login/` - User login with email/password
- `POST /auth/logout/` - User logout
- `GET /auth/user/` - Get current user info

### Conversation Endpoints
- `GET /conversations/` - List user's conversations
- `POST /conversations/` - Create new conversation
- `GET /conversations/<id>/` - Get specific conversation details
- `PUT /conversations/<id>/` - Update conversation (e.g., title)
- `DELETE /conversations/<id>/` - Delete conversation
- `GET /conversations/<id>/messages/` - Get all messages in conversation

### Updated Chat Endpoints
- `POST /chat/` - Send message (requires conversation_id, creates if none)
- `GET /chat/status/<task_id>/` - Poll for task status (unchanged)
- `POST /chat/clear/` - Clear current conversation context (modified)

## File Structure
```
backend/
├── api/
│   ├── chat_service.py          # Modified - Add user context & DB storage
│   ├── supabase_client.py       # Modified - Add conversation & message operations
│   ├── views.py                 # Modified - Add auth & conversation endpoints
│   ├── urls.py                  # Modified - Add new routes
│   └── management/
│       └── commands/
│           ├── create_admin_user.py     # New - Setup admin user
│           ├── migrate_leads.py         # New - Migrate existing leads
│           └── setup_supabase_tables.py # New - Create conversation tables
├── settings.py                  # Modified - Add auth configuration
└── requirements.txt             # No changes needed

frontend/
├── src/
│   ├── components/
│   │   ├── Login.js             # New - Login form component
│   │   ├── AuthContext.js       # New - Authentication context
│   │   ├── ConversationList.js  # New - Conversation history sidebar
│   │   ├── ConversationItem.js  # New - Individual conversation item
│   │   ├── ChatWidget.js        # Modified - Add sidebar & conversation management
│   │   ├── ChatWidget.css       # Modified - Add sidebar styling
│   │   ├── Header.js            # Modified - Add logout button
│   │   └── Login.css            # New - Login form styling
│   ├── services/
│   │   └── api.js               # Modified - Add conversation API calls
│   └── App.js                   # Modified - Add authentication wrapper
```

## Conversation Title Generation
- Use first user message as conversation title
- Truncate to 50 characters if longer
- Add "..." if truncated
- Default to "New Conversation" if first message is empty
- Update title automatically when first message is sent

## User Data Isolation
- All API endpoints filter data by current authenticated user
- Lead operations only affect user's own leads
- Conversation history only shows user's own conversations
- Default admin user owns all existing leads after migration
- No cross-user data access possible

## Authentication Flow
1. User visits any CRM page
2. If not authenticated, redirect to login page
3. User enters email/password
4. Django authenticates and creates session
5. User redirected to main CRM interface
6. All subsequent API calls include authentication
7. User can logout to clear session and return to login

This plan provides a comprehensive roadmap for implementing ChatGPT-style conversation history with user authentication while maintaining the existing chat functionality and ensuring proper data isolation between users. 