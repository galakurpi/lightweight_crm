# Lightweight CRM

A modern, lightweight Customer Relationship Management (CRM) system built with Django (backend) and React (frontend). Features a beautiful Kanban board interface for managing sales pipelines.

## Features

- 📊 **Kanban Board Interface** - Visual pipeline management with drag & drop
- 👥 **Lead Management** - Add, edit, and track customer leads
- 💰 **Deal Tracking** - Monitor deal values and progress
- 📱 **Responsive Design** - Works perfectly on desktop and mobile
- 🔄 **Real-time Updates** - Instant synchronization across the application
- 🎨 **Modern UI** - Clean, professional interface with smooth animations

## Tech Stack

### Backend
- **Django 4.2** - Python web framework
- **Django REST Framework** - API development
- **Supabase** - Database and real-time features
- **CORS Headers** - Cross-origin resource sharing

### Frontend
- **React 19** - Modern JavaScript framework
- **CSS3** - Custom styling with modern features
- **Fetch API** - HTTP client for API communication

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account (for database)
- Redis/Memurai (for chat functionality)
- OpenAI API key (for AI chat assistant)

### Backend Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd lightweight_crm
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   SUPABASE_URL=your-supabase-project-url
   SUPABASE_KEY=your-supabase-anon-key
   OPENAI_API_KEY=your-openai-api-key
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   DEBUG=True
   ```

5. **Run Django migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the required services:**
   
   You need to run 4 services simultaneously for the full application to work:

   **Terminal 1 - Start Memurai/Redis:**
   ```bash
   memurai
   # Or if you have Redis installed: redis-server
   ```

   **Terminal 2 - Start Celery Worker (from project root):**
   ```bash
   python -m celery -A backend.celery_app worker --loglevel=info --pool=solo
   ```

   **Terminal 3 - Start Django Backend:**
   ```bash
   cd backend
   python manage.py runserver
   ```

   **Terminal 4 - Start React Frontend:**
   ```bash
   cd frontend
   npm start
   ```

   The backend API will be available at `http://localhost:8000`
   The frontend will be available at `http://localhost:3000`

## Running the Application (Quick Reference)

### If Memurai/Redis is NOT running:
You need **4 terminals**:

1. **Terminal 1 - Memurai/Redis:**
   ```bash
   memurai
   ```

2. **Terminal 2 - Celery Worker:**
   ```bash
   cd "path/to/your/project/lightweight_crm"
   python -m celery -A backend.celery_app worker --loglevel=info --pool=solo
   ```

3. **Terminal 3 - Django Backend:**
   ```bash
   cd "path/to/your/project/lightweight_crm/backend"
   python manage.py runserver
   ```

4. **Terminal 4 - React Frontend:**
   ```bash
   cd "path/to/your/project/lightweight_crm/frontend"
   npm start
   ```

### If Memurai/Redis is ALREADY running:
Check if running: `netstat -ano | findstr :6379`

You only need **3 terminals**:

1. **Terminal 1 - Celery Worker:**
   ```bash
   cd "path/to/your/project/lightweight_crm"
   python -m celery -A backend.celery_app worker --loglevel=info --pool=solo
   ```

2. **Terminal 2 - Django Backend:**
   ```bash
   cd "path/to/your/project/lightweight_crm/backend"
   python manage.py runserver
   ```

3. **Terminal 3 - React Frontend:**
   ```bash
   cd "path/to/your/project/lightweight_crm/frontend"
   npm start
   ```

**Note:** The AI chat feature will only work when all required services are running!

## API Endpoints

### Leads Management
- `GET /leads/` - Get all leads (grouped by status)
- `POST /leads/` - Create a new lead
- `GET /leads/{id}/` - Get a specific lead
- `PUT /leads/{id}/` - Update a specific lead
- `DELETE /leads/{id}/` - Delete a specific lead
- `PUT /leads/{id}/status/` - Update lead status (for Kanban moves)

### Chat/AI Assistant
- `POST /chat/` - Send message to AI assistant
- `GET /chat/status/{task_id}/` - Poll for chat task status
- `POST /chat/clear/` - Clear conversation context

### Test Endpoint
- `GET /test/` - Test API connectivity

## Database Schema

The application uses a `leads` table with the following structure:

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    value DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Interest',
    notes TEXT,
    source VARCHAR(100),
    card_order INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Lead Status Options

The CRM supports the following lead statuses:
- **Interest** - Initial contact or inquiry
- **Meeting booked** - Meeting scheduled with prospect
- **Proposal sent** - Formal proposal submitted
- **Closed win** - Deal successfully closed
- **Closed lost** - Deal lost or rejected

## Development

### Project Structure
```
lightweight_crm/
├── backend/                 # Django backend
│   ├── api/                # API application
│   │   ├── views.py        # API endpoints
│   │   ├── urls.py         # URL routing
│   │   └── supabase_client.py  # Database client
│   ├── settings.py         # Django settings
│   └── urls.py            # Main URL configuration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Header.js   # App header
│   │   │   ├── KanbanBoard.js  # Main board
│   │   │   ├── LeadCard.js     # Individual lead cards
│   │   │   └── LeadForm.js     # Add/edit lead form
│   │   ├── App.js          # Main app component
│   │   └── App.css         # Global styles
│   └── public/             # Static assets
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Adding New Features

1. **Backend**: Add new API endpoints in `backend/api/views.py` and register them in `backend/api/urls.py`
2. **Frontend**: Create new components in `frontend/src/components/` and import them in `App.js`
3. **Database**: Use Supabase dashboard to modify the database schema

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_KEY` | Your Supabase anon key | Yes |
| `OPENAI_API_KEY` | OpenAI API key for chat functionality | Yes |
| `CELERY_BROKER_URL` | Redis/Memurai URL for Celery | No (default: redis://localhost:6379/0) |
| `CELERY_RESULT_BACKEND` | Redis/Memurai URL for results | No (default: redis://localhost:6379/0) |
| `DEBUG` | Django debug mode | No (default: False) |
| `REACT_APP_API_URL` | Backend API URL for frontend | No (default: http://localhost:8000) |

## Deployment

### Backend Deployment
1. Set `DEBUG=False` in production
2. Configure allowed hosts in Django settings
3. Use a production WSGI server like Gunicorn
4. Set up proper environment variables

### Frontend Deployment
1. Build the React app: `npm run build`
2. Serve the built files with a web server
3. Configure the API URL for production

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and commit them
4. Push to your fork and submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please create an issue in the GitHub repository. 