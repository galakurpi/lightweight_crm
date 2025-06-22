import React, { useState } from 'react';
import './KanbanBoard.css';
import LeadCard from './LeadCard';
import LeadDetailsModal from './LeadDetailsModal';

const KanbanBoard = ({ leads, onUpdateLeadStatus, onDeleteLead, onUpdateLead, onAddLead }) => {
  const [selectedLead, setSelectedLead] = useState(null);

  const statusColumns = [
    { key: 'Interest', title: 'Interest', color: '#74b9ff' },
    { key: 'Meeting booked', title: 'Meeting Booked', color: '#fdcb6e' },
    { key: 'Proposal sent', title: 'Proposal Sent', color: '#e17055' },
    { key: 'Closed win', title: 'Closed Win', color: '#00b894' },
    { key: 'Closed lost', title: 'Closed Lost', color: '#fd79a8' }
  ];

  const handleDragStart = (e, leadId, currentStatus) => {
    e.dataTransfer.setData('text/plain', JSON.stringify({
      leadId,
      currentStatus
    }));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e, newStatus) => {
    e.preventDefault();
    const data = JSON.parse(e.dataTransfer.getData('text/plain'));
    
    if (data.currentStatus !== newStatus) {
      // Calculate new order (place at end of column)
      const newOrder = (leads[newStatus] || []).length + 1;
      onUpdateLeadStatus(data.leadId, newStatus, newOrder);
    }
  };

  const handleLeadDoubleClick = (lead) => {
    setSelectedLead(lead);
  };

  const handleCloseModal = () => {
    setSelectedLead(null);
  };

  const handleUpdateLead = async (leadId, updateData) => {
    try {
      await onUpdateLead(leadId, updateData);
      // Update the selected lead with the new data for immediate UI feedback
      setSelectedLead(prev => ({ ...prev, ...updateData }));
    } catch (error) {
      console.error('Error updating lead:', error);
      throw error;
    }
  };

  const handleAddToColumn = (status) => {
    // Call the onAddLead function with the specific status
    onAddLead(status);
  };

  return (
    <>
      <div className="kanban-board">
        <div className="kanban-columns">
          {statusColumns.map(column => (
            <div 
              key={column.key}
              className="kanban-column"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, column.key)}
            >
              <div 
                className="column-header"
                style={{ borderTopColor: column.color }}
              >
                <h3 className="column-title">{column.title}</h3>
                <span className="column-count">
                  {(leads[column.key] || []).length}
                </span>
              </div>
              
              <div className="column-content">
                {(leads[column.key] || []).map(lead => (
                  <LeadCard
                    key={lead.id}
                    lead={lead}
                    onDragStart={(e) => handleDragStart(e, lead.id, column.key)}
                    onDelete={() => onDeleteLead(lead.id)}
                    onDoubleClick={handleLeadDoubleClick}
                    statusColor={column.color}
                  />
                ))}
                
                {(leads[column.key] || []).length === 0 && (
                  <div className="empty-column">
                    <p>No leads in this stage</p>
                    <small>Drag leads here or add new ones</small>
                  </div>
                )}
                
                <button 
                  className="add-to-column-btn"
                  onClick={() => handleAddToColumn(column.key)}
                  title={`Add lead to ${column.title}`}
                >
                  <span className="add-btn-icon">+</span>
                  <span className="add-btn-text">Add Lead</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {selectedLead && (
        <LeadDetailsModal
          lead={selectedLead}
          onClose={handleCloseModal}
          onUpdate={handleUpdateLead}
        />
      )}
    </>
  );
};

export default KanbanBoard; 