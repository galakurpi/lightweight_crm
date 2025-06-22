import React from 'react';
import './ChatWidget.css';

const ChatButton = ({ isOpen, onClick, hasUnreadMessages = false }) => {
  return (
    <button 
      className={`chat-button ${isOpen ? 'open' : ''}`}
      onClick={onClick}
      aria-label={isOpen ? 'Close chat' : 'Open chat'}
    >
      {isOpen ? (
        // Close icon (X)
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      ) : (
        // Chat icon with notification badge
        <div className="chat-icon-container">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
          </svg>
          {hasUnreadMessages && <div className="notification-badge"></div>}
        </div>
      )}
    </button>
  );
};

export default ChatButton; 