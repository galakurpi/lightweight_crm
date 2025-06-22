import React from 'react';
import './ChatWidget.css';

const ChatMessage = ({ message, isUser, timestamp, isLoading = false }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  };

  if (isLoading) {
    return (
      <div className="chat-message ai-message">
        <div className="message-content">
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
          <span className="typing-text">AI is thinking...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'}`}>
      <div className="message-content">
        <div className="message-text">{message}</div>
        {timestamp && (
          <div className="message-timestamp">{formatTime(timestamp)}</div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage; 