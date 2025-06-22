# Frontend Documentation - Lightweight CRM

## Overview

The frontend is a modern React 19.1.0 application providing a Kanban-style CRM interface with integrated AI chat assistant. Built with component-based architecture, it follows modern React patterns and includes automatic light/dark theme switching with localStorage persistence.

## Architecture

### Tech Stack
- **React**: 19.1.0 - Main UI framework
- **React Scripts**: 5.0.1 - Build tooling and development server
- **CSS**: Vanilla CSS with component-specific stylesheets
- **Testing**: React Testing Library + Jest
- **HTTP**: Native Fetch API for backend communication

### Project Structure
```
frontend/src/
├── App.js                    # Main application component and state management
├── App.css                   # Global styles and utilities
├── index.js                  # React app entry point
└── components/
    ├── Header.js/css         # Navigation bar with theme toggle
    ├── KanbanBoard.js/css    # Main CRM board with drag-and-drop
    ├── LeadCard.js/css       # Individual lead cards
    ├── LeadForm.js/css       # Add/edit lead form modal
    ├── LeadDetailsModal.js/css # Lead details and editing modal
    ├── ChatWidget.js/css     # AI chat interface
    ├── ChatButton.js         # Floating chat toggle button
    └── ChatMessage.js        # Individual chat message component
```

## Core Components

### App.js - Main Application Controller
Root component managing global state, API communication, error handling, and component orchestration.

**Key State:**
```javascript
const [leads, setLeads] = useState({
  'Interest': [], 'Meeting booked': [], 'Proposal sent': [],
  'Closed win': [], 'Closed lost': []
});
const [showAddForm, setShowAddForm] = useState(false);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

**API Methods:** fetchLeads(), addLead(), updateLeadStatus(), updateLead(), deleteLead()

### KanbanBoard.js - Main CRM Interface
Drag-and-drop Kanban board with five status columns:
1. **Interest** (#74b9ff), **Meeting Booked** (#fdcb6e), **Proposal Sent** (#e17055)
2. **Closed Win** (#00b894), **Closed Lost** (#fd79a8)

**Features:** HTML5 drag-and-drop, lead counts, quick add buttons, double-click details, empty state messaging

### LeadCard.js - Individual Lead Display
Compact card with avatar generation, color coding, drag functionality, delete button, and double-click details.

### LeadForm.js - Lead Creation/Editing
Modal form with validation for Name* (required), Company, Email* (required, validated), Phone, Deal Value (numeric), Notes, Status, and Source dropdowns.

**Source Options:** Website, Referral, Social Media, Cold Call, Email Campaign, Trade Show, Other

### LeadDetailsModal.js - Detailed Lead View
Full-featured modal with read-only view, edit mode, status updates, delete confirmation, and responsive design.

### ChatWidget.js - AI Assistant Interface
300x400px floating chat with session-based context, async processing, 2-second polling, message history, typing indicators, and error handling.

**Flow:** User message → POST /chat/ → Poll /chat/status/{task_id}/ → Display result

### Header.js - Navigation Bar
CRM title, refresh/add buttons, and day/night theme toggle with sun/moon icons.

## Styling & Design

### CSS Organization
- Global styles in App.css, component-specific stylesheets, BEM-like naming, mobile-first responsive design

### Design System
**Colors:** Primary #6c5ce7, Success #00b894, Warning #fdcb6e, Danger #ff7675
**Theme:** Light/dark mode with CSS custom properties, localStorage persistence, smooth transitions
**Typography:** System font stack, antialiased rendering, consistent hierarchy
**Layout:** Flexbox/Grid, consistent spacing (0.5rem, 1rem, 2rem), border-box sizing

### Accessibility
Focus indicators, keyboard navigation, semantic HTML, ARIA attributes, WCAG color contrast, responsive design

## State Management

### Component State
React hooks: `useState`, `useEffect`, `useRef`

### Global State Flow
```
App.js → leads/error/loading/form state
Components ← data/action/state props
```

### API State
Optimistic updates, error recovery, loading states, cache invalidation

## API Integration

**Base URL:** `process.env.REACT_APP_API_URL || 'http://localhost:8000'`
**Patterns:** REST endpoints, JSON format, HTTP status handling, error parsing
**Chat:** Task-based async processing with polling, session cookies

## Development

### Getting Started
```bash
cd frontend
npm install
npm start  # http://localhost:3000
```

### Scripts
- `npm start` - Development server with hot reload
- `npm build` - Production build
- `npm test` - Test suite

### Component Design
1. Single responsibility, clean props interface, error boundaries, performance optimization
2. Functional components, custom hooks, consistent event naming, extracted constants

### Error Handling
User-friendly messages, graceful degradation, retry mechanisms, error boundaries

## Browser Support
Chrome, Firefox, Safari, Edge (latest 2 versions)
Includes ES6+, Fetch API, Promises polyfills

## Deployment
```bash
npm run build  # Creates optimized build/ directory
```
Static HTML/CSS/JS files with asset hashing, gzip compression recommended, CDN compatible

## Testing & Performance

### Testing
Component/integration tests, API mocking, accessibility testing with React Testing Library + Jest

### Performance
Component memoization, lazy loading, asset optimization, API efficiency
Bundle analysis, source maps, tree shaking included

## Troubleshooting

**Common Issues:**
1. CORS errors → Check backend CORS config
2. API connection → Verify REACT_APP_API_URL
3. Build failures → Clear node_modules, reinstall
4. Performance → Check useEffect cleanup

**Debug Tools:** React DevTools, Network tab, console logs, error boundaries

## Future Enhancements

**Improvements:** Redux/Zustand state management, TypeScript, E2E testing, virtual scrolling, PWA, i18n, enhanced theming

**Architecture:** Micro-frontends, component library, design system, analytics integration

## Contributing

**Code Style:** Prettier formatting, ESLint rules, consistent naming, documented complex logic

**Process:** Feature branch → Tests → Documentation → Code review → Merge

This documentation enables developers and AI assistants to effectively work with and extend the CRM application.