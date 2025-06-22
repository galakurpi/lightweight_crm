const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'frontend/build')));

// API Routes - Basic placeholder routes for now
// In a real deployment, these would connect to your database
app.get('/leads/', (req, res) => {
  // Placeholder response matching your API structure
  res.json({
    "Interest": [],
    "Meeting booked": [],
    "Proposal sent": [],
    "Closed win": [],
    "Closed lost": []
  });
});

app.post('/leads/', (req, res) => {
  // Placeholder for creating leads
  const leadData = req.body;
  res.status(201).json({
    id: Date.now().toString(),
    ...leadData,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  });
});

app.get('/leads/:id', (req, res) => {
  // Placeholder for getting individual lead
  res.json({
    id: req.params.id,
    name: "Sample Lead",
    company: "Sample Company",
    status: "Interest"
  });
});

app.put('/leads/:id', (req, res) => {
  // Placeholder for updating lead
  res.json({
    id: req.params.id,
    ...req.body,
    updated_at: new Date().toISOString()
  });
});

app.delete('/leads/:id', (req, res) => {
  // Placeholder for deleting lead
  res.status(204).send();
});

app.put('/leads/:id/status/', (req, res) => {
  // Placeholder for updating lead status
  res.json({
    id: req.params.id,
    ...req.body,
    updated_at: new Date().toISOString()
  });
});

// Chat endpoints - Simplified without OpenAI for initial deployment
app.post('/chat/', (req, res) => {
  // Placeholder chat response
  res.json({
    task_id: Date.now().toString(),
    status: 'processing',
    message: 'Message received, processing...'
  });
});

app.get('/chat/status/:taskId', (req, res) => {
  // Placeholder chat status
  res.json({
    state: 'SUCCESS',
    result: {
      ai_message: 'This is a placeholder response. The full AI functionality requires OpenAI API integration.',
      function_results: [],
      status: 'success'
    }
  });
});

app.post('/chat/clear/', (req, res) => {
  res.json({ message: 'Chat cleared successfully' });
});

app.get('/test/', (req, res) => {
  res.json({
    message: 'Node.js API is working!',
    status: 'success'
  });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
}); 