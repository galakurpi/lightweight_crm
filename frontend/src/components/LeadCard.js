import React from 'react';
import './LeadCard.css';

const LeadCard = ({ lead, onDragStart, onDelete, onDoubleClick, statusColor }) => {
  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div 
      className="lead-card"
      draggable
      onDragStart={onDragStart}
      onDoubleClick={() => onDoubleClick(lead)}
      style={{ borderLeftColor: statusColor }}
      title="Double-click to view details"
    >
      <div className="lead-card-header">
        <div className="lead-avatar">
          {getInitials(lead.name)}
        </div>
        <div className="lead-info">
          <h4 className="lead-name">{lead.name || 'Unnamed Lead'}</h4>
          <p className="lead-company">{lead.company || 'No company'}</p>
        </div>
        <button 
          className="delete-btn"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          title="Delete lead"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default LeadCard; 