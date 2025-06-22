import React, { useState, useEffect } from 'react';
import ConversationItem from './ConversationItem';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ConversationList = ({ 
  selectedConversationId, 
  onSelectConversation, 
  onNewConversation,
  refreshTrigger 
}) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load conversations
  useEffect(() => {
    loadConversations();
  }, [refreshTrigger]);

  const loadConversations = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/conversations/`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      } else if (response.status === 401) {
        setError('Authentication required');
      } else {
        setError('Failed to load conversations');
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConversation = async (conversationId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (response.ok) {
        // Remove from local state
        setConversations(prev => prev.filter(conv => conv.id !== conversationId));
        
        // If this was the selected conversation, clear selection
        if (selectedConversationId === conversationId) {
          onSelectConversation(null);
        }
      } else {
        console.error('Failed to delete conversation');
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleUpdateConversation = async (conversationId, updates) => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        const updatedConversation = await response.json();
        setConversations(prev => 
          prev.map(conv => 
            conv.id === conversationId ? updatedConversation : conv
          )
        );
      } else {
        console.error('Failed to update conversation');
      }
    } catch (error) {
      console.error('Error updating conversation:', error);
    }
  };

  if (loading) {
    return (
      <div className="conversation-list">
        <div className="conversation-list-header">
          <h3>Conversations</h3>
          <button 
            className="new-conversation-btn"
            onClick={onNewConversation}
            title="Start new conversation"
          >
            ✏️
          </button>
        </div>
        <div className="conversation-list-loading">
          <div className="loading-spinner"></div>
          <p>Loading conversations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="conversation-list">
        <div className="conversation-list-header">
          <h3>Conversations</h3>
          <button 
            className="new-conversation-btn"
            onClick={onNewConversation}
            title="Start new conversation"
          >
            ✏️
          </button>
        </div>
        <div className="conversation-list-error">
          <p>{error}</p>
          <button onClick={loadConversations} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-list">
      <div className="conversation-list-header">
        <h3>Conversations</h3>
        <button 
          className="new-conversation-btn"
          onClick={onNewConversation}
          title="Start new conversation"
        >
          ✏️
        </button>
      </div>
      
      <div className="conversation-list-content">
        {conversations.length === 0 ? (
          <div className="no-conversations">
            <p>No conversations yet</p>
            <button 
              className="start-conversation-btn"
              onClick={onNewConversation}
            >
              Start your first conversation
            </button>
          </div>
        ) : (
          <div className="conversations-scroll">
            {conversations.map(conversation => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isSelected={selectedConversationId === conversation.id}
                onSelect={() => onSelectConversation(conversation.id)}
                onDelete={() => handleDeleteConversation(conversation.id)}
                onUpdate={(updates) => handleUpdateConversation(conversation.id, updates)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConversationList; 