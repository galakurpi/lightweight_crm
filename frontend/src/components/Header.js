import React from 'react';
import './Header.css';

const Header = ({ onAddLead, onRefresh }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">
            <span className="header-icon">📊</span>
            Lightweight CRM
          </h1>
          <p className="header-subtitle">Manage your sales pipeline efficiently</p>
        </div>
        
        <div className="header-actions">
          <button 
            className="btn btn-secondary"
            onClick={onRefresh}
            title="Refresh leads"
          >
            🔄 Refresh
          </button>
          <button 
            className="btn btn-primary"
            onClick={onAddLead}
          >
            + Add Lead
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 