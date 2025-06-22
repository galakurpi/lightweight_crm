import React, { useState, useEffect } from 'react';
import './App.css';
import KanbanBoard from './components/KanbanBoard';
import LeadForm from './components/LeadForm';
import Header from './components/Header';
import ChatWidget from './components/ChatWidget';

// Base API URL for the Django backend
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [leads, setLeads] = useState({
    'Interest': [],
    'Meeting booked': [],
    'Proposal sent': [],
    'Closed win': [],
    'Closed lost': []
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const [defaultStatus, setDefaultStatus] = useState('Interest');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch leads from Django backend
  const fetchLeads = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/leads/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLeads(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching leads:', err);
      setError('Failed to fetch leads. Please check if the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  // Add new lead
  const addLead = async (leadData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leads/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leadData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh leads after adding
      await fetchLeads();
      setShowAddForm(false);
    } catch (err) {
      console.error('Error adding lead:', err);
      setError('Failed to add lead. Please try again.');
    }
  };

  // Handle adding lead with specific status
  const handleAddLead = (status = 'Interest') => {
    setDefaultStatus(status);
    setShowAddForm(true);
  };

  // Update lead status (for drag & drop)
  const updateLeadStatus = async (leadId, newStatus, newOrder) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leads/${leadId}/status/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus,
          card_order: newOrder
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh leads after updating
      await fetchLeads();
    } catch (err) {
      console.error('Error updating lead status:', err);
      setError('Failed to update lead status. Please try again.');
    }
  };

  // Update lead (for editing lead details)
  const updateLead = async (leadId, leadData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leads/${leadId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leadData),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh leads after updating
      await fetchLeads();
    } catch (err) {
      console.error('Error updating lead:', err);
      setError('Failed to update lead. Please try again.');
      throw err; // Re-throw to handle in the modal
    }
  };

  // Delete lead
  const deleteLead = async (leadId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/leads/${leadId}/`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Refresh leads after deleting
      await fetchLeads();
    } catch (err) {
      console.error('Error deleting lead:', err);
      setError('Failed to delete lead. Please try again.');
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  if (loading) {
    return (
      <div className="App">
        <div className="loading">Loading CRM...</div>
      </div>
    );
  }

  return (
    <div className="App">
      <Header 
        onAddLead={() => handleAddLead()}
        onRefresh={fetchLeads}
      />
      
      {error && (
        <div className="error-banner">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}
      
      <main className="main-content">
        <KanbanBoard 
          leads={leads}
          onUpdateLeadStatus={updateLeadStatus}
          onDeleteLead={deleteLead}
          onUpdateLead={updateLead}
          onAddLead={handleAddLead}
        />
      </main>
      
      {showAddForm && (
        <LeadForm 
          onSubmit={addLead}
          onCancel={() => setShowAddForm(false)}
          defaultStatus={defaultStatus}
        />
      )}
      
      <ChatWidget />
    </div>
  );
}

export default App;
