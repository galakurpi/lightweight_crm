import React from 'react';
import './ChatWidget.css';

const ChatMessage = ({ message, isUser, timestamp, isLoading = false, isConfirmationRequest = false, functionResults = [], onConfirmAction }) => {
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

  // Extract lead name from delete_lead function result for confirmation buttons
  const getLeadNameFromConfirmation = () => {
    if (!isConfirmationRequest || !functionResults) return null;
    
    const deleteResult = functionResults.find(result => 
      result.function === 'delete_lead' && result.result && result.result.requires_confirmation
    );
    
    if (deleteResult && deleteResult.arguments && deleteResult.arguments.lead_id) {
      // Try to extract lead name from the message
      const messageText = message || '';
      const nameMatch = messageText.match(/'([^']+)'/);
      return nameMatch ? nameMatch[1] : 'this lead';
    }
    
    return null;
  };

  const leadName = getLeadNameFromConfirmation();

  return (
    <div className={`chat-message ${isUser ? 'user-message' : 'ai-message'} ${isConfirmationRequest ? 'confirmation-message' : ''}`}>
      <div className="message-content">
        <div className="message-text">{message}</div>
        
        {isConfirmationRequest && leadName && onConfirmAction && (
          <div className="confirmation-actions">
            <button 
              className="confirm-btn confirm-yes"
              onClick={() => onConfirmAction(`yes, delete ${leadName}`)}
              title="Confirm deletion"
            >
              ✓ Yes, Delete
            </button>
            <button 
              className="confirm-btn confirm-no"
              onClick={() => onConfirmAction('cancel deletion')}
              title="Cancel deletion"
            >
              ✗ Cancel
            </button>
          </div>
        )}
        
        {timestamp && (
          <div className="message-timestamp">{formatTime(timestamp)}</div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage; 