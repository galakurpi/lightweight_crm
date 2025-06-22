import React from 'react';
import { useAuth } from './AuthContext';
import './Header.css';

const Header = ({ onAddLead, onRefresh, isDarkMode, onToggleTheme }) => {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
    }
  };
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1 className="header-title">
            <span className="header-icon">📊</span>
            Lightweight CRM
          </h1>
          <p className="header-subtitle">
            Welcome, {user?.first_name || user?.email || 'User'} | Manage your sales pipeline efficiently
          </p>
        </div>
        
        <div className="header-actions">
          <button 
            className="btn btn-theme-toggle"
            onClick={onToggleTheme}
            title={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDarkMode ? '☀️' : '🌙'}
          </button>
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
          <button 
            className="btn btn-logout"
            onClick={handleLogout}
            title="Logout"
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 