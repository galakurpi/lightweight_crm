# Frontend Documentation - Lightweight CRM

## Overview

- Modern React app with Kanban CRM, AI chat assistant, and day/night mode toggle
- Users can switch between light and dark themes; preference is saved automatically

The frontend is a modern React application built with React 19.1.0 that provides a Kanban-style CRM interface with an integrated AI chat assistant. The application uses a component-based architecture with clean separation of concerns and follows modern React patterns including hooks, functional components, and state management.

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
├── index.css                 # Base CSS styles
└── components/
    ├── Header.js/css         # Top navigation bar
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
The root component that manages:
- **Global State**: Leads data organized by status columns
- **API Communication**: All backend interactions for CRUD operations
- **Error Handling**: Global error state and user feedback
- **Component Orchestration**: Renders and coordinates all child components

**Key State Variables:**
```javascript
const [leads, setLeads] = useState({
  'Interest': [],
  'Meeting booked': [],
  'Proposal sent': [],
  'Closed win': [],
  'Closed lost': []
});
const [showAddForm, setShowAddForm] = useState(false);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

**API Integration:**
- `fetchLeads()` - GET /leads/ - Retrieves all leads organized by status
- `addLead()` - POST /leads/ - Creates new lead
- `updateLeadStatus()` - PUT /leads/{id}/status/ - Updates lead status and order
- `updateLead()` - PUT /leads/{id}/ - Updates lead details
- `deleteLead()` - DELETE /leads/{id}/ - Removes lead

### KanbanBoard.js - Main CRM Interface
Implements a drag-and-drop Kanban board with five status columns:

**Status Columns:**
1. **Interest** (#74b9ff) - Initial lead stage
2. **Meeting Booked** (#fdcb6e) - Meeting scheduled
3. **Proposal Sent** (#e17055) - Proposal delivered
4. **Closed Win** (#00b894) - Deal won
5. **Closed Lost** (#fd79a8) - Deal lost

**Features:**
- **Drag & Drop**: HTML5 drag-and-drop API for moving leads between columns
- **Lead Count**: Real-time count display for each column
- **Quick Add**: Column-specific "Add Lead" buttons
- **Double-click Details**: Opens detailed lead modal
- **Empty State**: Helpful messaging when columns are empty

**Drag & Drop Implementation:**
```javascript
const handleDragStart = (e, leadId, currentStatus) => {
  e.dataTransfer.setData('text/plain', JSON.stringify({
    leadId, currentStatus
  }));
};

const handleDrop = (e, newStatus) => {
  e.preventDefault();
  const data = JSON.parse(e.dataTransfer.getData('text/plain'));
  if (data.currentStatus !== newStatus) {
    const newOrder = (leads[newStatus] || []).length + 1;
    onUpdateLeadStatus(data.leadId, newStatus, newOrder);
  }
};
```

### LeadCard.js - Individual Lead Display
Compact card component representing a single lead:

**Features:**
- **Avatar Generation**: Automatic initials from lead name
- **Color Coding**: Left border matches column status color
- **Drag Handle**: Entire card is draggable
- **Quick Actions**: Delete button with confirmation
- **Double-click**: Opens detailed view

**Data Display:**
- Lead name (with fallback to "Unnamed Lead")
- Company name (with fallback to "No company")
- Visual status indicator via border color

### LeadForm.js - Lead Creation/Editing
Modal form for adding new leads with comprehensive validation:

**Form Fields:**
- **Name*** (required) - Lead contact name
- **Company** - Organization name
- **Email*** (required, validated) - Contact email
- **Phone** - Contact phone number
- **Deal Value** - Potential revenue (numeric validation)
- **Notes** - Additional information
- **Status** - Pipeline stage (dropdown)
- **Source** - Lead origin (dropdown)

**Validation Rules:**
- Name: Required, non-empty
- Email: Required, valid email format
- Deal Value: Must be numeric if provided
- Real-time validation feedback
- Error state styling

**Source Options:**
Website, Referral, Social Media, Cold Call, Email Campaign, Trade Show, Other

### LeadDetailsModal.js - Detailed Lead View
Full-featured modal for viewing and editing lead details:

**Features:**
- **Read-only View**: Clean presentation of all lead information
- **Edit Mode**: In-place editing with form validation
- **Status Updates**: Dropdown for changing pipeline stage
- **Delete Confirmation**: Two-step deletion process
- **Responsive Design**: Adapts to different screen sizes

### ChatWidget.js - AI Assistant Interface
Floating chat interface with asynchronous AI processing:

**Architecture:**
- **Minimalist Design**: 300x400px expandable interface
- **Session-based Context**: Conversation memory via Django sessions
- **Async Processing**: Background task handling with polling
- **Real-time Updates**: Status polling every 2 seconds

**Key Features:**
- **Floating Button**: Bottom-right corner toggle
- **Message History**: Persistent conversation display
- **Typing Indicators**: Loading states during AI processing
- **Clear Conversation**: Manual context reset
- **Error Handling**: Connection and processing error recovery

**Async Flow:**
1. User sends message → POST /chat/ returns task_id
2. Frontend polls GET /chat/status/{task_id}/ every 2 seconds
3. Task completion triggers message display
4. Error states handled gracefully

### Header.js - Navigation Bar
- CRM title, subtitle, refresh and add lead buttons
- Includes a day/night mode toggle button for switching between light and dark themes
- Toggle uses sun/moon icons and updates the theme instantly

## Styling Architecture

### CSS Organization
- **Global Styles**: App.css contains utility classes and base styles
- **Component Styles**: Each component has its own CSS file
- **Consistent Naming**: BEM-like naming convention
- **Responsive Design**: Mobile-first approach with media queries

### Design System
**Colors:**
- Primary: #6c5ce7 (purple)
- Success: #00b894 (green)
- Warning: #fdcb6e (yellow)
- Danger: #ff7675 (red)
- Text: #2d3436 (dark gray)
- Background: #f8f9fa (light gray)
- Supports both light and dark color schemes via theme toggle
- Theme is managed with CSS custom properties and transitions for a smooth experience

**User Experience:**
- Theme preference is stored in localStorage and applied on future visits
- All UI components adapt colors and backgrounds based on the selected theme

**Typography:**
- Font Stack: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- Font Smoothing: Antialiased for better rendering
- Consistent sizing hierarchy

**Layout Patterns:**
- Flexbox for component layouts
- CSS Grid for complex arrangements
- Consistent spacing scale (0.5rem, 1rem, 2rem)
- Box-sizing: border-box globally

### Accessibility Features
- **Focus Management**: Visible focus indicators
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: Semantic HTML and ARIA attributes
- **Color Contrast**: WCAG compliant color combinations
- **Responsive Design**: Works on all device sizes

## State Management

### Local Component State
Each component manages its own UI state using React hooks:
- `useState` for simple state values
- `useEffect` for side effects and lifecycle events
- `useRef` for DOM references and mutable values

### Global State Flow
State flows down from App.js to child components via props:

```
App.js (global state)
├── leads data
├── error state
├── loading state
└── form visibility

Components receive:
├── Data props (leads, selectedLead)
├── Action props (onAdd, onUpdate, onDelete)
└── State props (loading, error)
```

### API State Management
- **Optimistic Updates**: UI updates immediately, then syncs with backend
- **Error Recovery**: Failed operations revert UI state
- **Loading States**: Visual feedback during async operations
- **Cache Invalidation**: Refresh data after mutations

## Development Patterns

### Component Design Principles
1. **Single Responsibility**: Each component has one clear purpose
2. **Props Interface**: Clean, predictable prop contracts
3. **Error Boundaries**: Graceful error handling
4. **Performance**: Minimal re-renders, efficient updates

### Code Organization
- **Functional Components**: All components use function syntax
- **Custom Hooks**: Reusable stateful logic (potential for extraction)
- **Event Handling**: Consistent naming (handle*, on*)
- **Constants**: Extracted to top of files or separate modules

### Error Handling Strategy
- **User-Friendly Messages**: Clear, actionable error text
- **Graceful Degradation**: Partial functionality when possible
- **Retry Mechanisms**: Automatic and manual retry options
- **Error Boundaries**: Prevent cascading failures

## API Integration

### Backend Communication
**Base URL Configuration:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**Standard API Patterns:**
- REST endpoints for CRUD operations
- JSON request/response format
- HTTP status code handling
- Error response parsing

**Async Patterns:**
- Chat API uses task-based async processing
- Polling for long-running operations
- Session cookies for authentication

### Environment Configuration
- **Development**: http://localhost:8000 (Django dev server)
- **Production**: Configurable via REACT_APP_API_URL
- **CORS**: Handled by Django backend configuration

## Testing Strategy

### Test Setup
- **React Testing Library**: Component testing framework
- **Jest**: Test runner and assertion library
- **User Event**: Simulated user interactions
- **DOM Testing**: Focus on user behavior over implementation

### Testing Patterns
- **Component Tests**: Render and interaction testing
- **Integration Tests**: Multi-component workflows
- **API Mocking**: Isolated frontend testing
- **Accessibility Tests**: Screen reader and keyboard testing

## Performance Considerations

### Optimization Techniques
- **Component Memoization**: Prevent unnecessary re-renders
- **Lazy Loading**: Code splitting for larger features
- **Asset Optimization**: Image and bundle size optimization
- **API Efficiency**: Minimal data fetching, batch operations

### Bundle Analysis
- React Scripts provides built-in bundle analysis
- Source map generation for debugging
- Tree shaking for unused code elimination

## Development Workflow

### Getting Started
```bash
cd frontend
npm install
npm start  # Development server on http://localhost:3000
```

### Available Scripts
- `npm start` - Development server with hot reload
- `npm build` - Production build
- `npm test` - Run test suite
- `npm run eject` - Eject from Create React App (not recommended)

### Development Server
- **Hot Reload**: Automatic page refresh on file changes
- **Error Overlay**: In-browser error display
- **Development Tools**: React DevTools integration
- **Proxy Configuration**: API requests proxied to backend

## Browser Support

### Supported Browsers
- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

### Polyfills
React Scripts includes necessary polyfills for:
- ES6+ features
- Fetch API
- Promises
- Array methods

## Deployment

### Build Process
```bash
npm run build
```
Creates optimized production build in `build/` directory.

### Static File Serving
- **Build Output**: Static HTML, CSS, JS files
- **Asset Hashing**: Automatic cache busting
- **Compression**: Gzip compression recommended
- **CDN Compatible**: Static assets can be served from CDN

## Future Enhancements

### Potential Improvements
1. **State Management**: Consider Redux/Zustand for complex state
2. **TypeScript**: Add type safety for larger development teams
3. **Testing**: Increase test coverage, add E2E tests
4. **Performance**: Implement virtual scrolling for large datasets
5. **PWA**: Add service worker for offline functionality
6. **Internationalization**: Multi-language support
7. **Theming**: Dark mode and customizable themes

### Architectural Considerations
- **Micro-frontends**: Potential for splitting into smaller apps
- **Component Library**: Extract reusable components
- **Design System**: Formal design system implementation
- **Analytics**: User behavior tracking integration

## Troubleshooting

### Common Issues
1. **CORS Errors**: Check backend CORS configuration
2. **API Connection**: Verify REACT_APP_API_URL environment variable
3. **Build Failures**: Clear node_modules and reinstall dependencies
4. **Performance**: Check for memory leaks in useEffect cleanup

### Debug Tools
- **React DevTools**: Component inspection and profiling
- **Network Tab**: API request/response debugging
- **Console Logs**: Strategic logging for state changes
- **Error Boundaries**: Catch and display component errors

## Contributing Guidelines

### Code Style
- **Formatting**: Prettier configuration (if added)
- **Linting**: ESLint rules from Create React App
- **Naming**: Consistent component and function naming
- **Comments**: Document complex logic and business rules

### Pull Request Process 
1. Feature branch from main
2. Component and integration tests
3. Update documentation if needed
4. Code review and approval
5. Merge to main branch

This documentation provides a comprehensive overview of the frontend architecture and should enable developers and AI assistants to effectively work with and extend the CRM application.