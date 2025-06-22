import React, { useState, useEffect, useRef } from 'react';
import ChatButton from './ChatButton';
import ChatMessage from './ChatMessage';
import './ChatWidget.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatWidget = ({ onLeadsUpdated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const messagesEndRef = useRef(null);
  const pollingIntervalRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Clean up polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  // Poll for task status
  const pollTaskStatus = (taskId) => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    pollingIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/status/${taskId}/`);
        const data = await response.json();

        if (data.state === 'SUCCESS') {
          clearInterval(pollingIntervalRef.current);
          setIsLoading(false);
          setCurrentTaskId(null);

          // Add AI response to messages
          if (data.result && data.result.ai_message) {
            // Check if this is a deletion confirmation request
            const isConfirmationRequest = data.result.function_results && 
              data.result.function_results.some(result => 
                result.function === 'delete_lead' && 
                result.result && 
                result.result.requires_confirmation
              );

            // Debug logging
            console.log('AI Response:', data.result);
            console.log('Function Results:', data.result.function_results);
            console.log('Is Confirmation Request:', isConfirmationRequest);
            if (data.result.function_results) {
              data.result.function_results.forEach((result, index) => {
                console.log(`Function ${index}:`, result.function, 'Success:', result.result?.success, 'Requires Confirmation:', result.result?.requires_confirmation);
              });
            }

            setMessages(prev => [...prev, {
              id: Date.now(),
              message: data.result.ai_message,
              isUser: false,
              timestamp: new Date().toISOString(),
              isConfirmationRequest: isConfirmationRequest,
              functionResults: data.result.function_results
            }]);
          }

          // Check if any lead operations were performed and refresh leads
          if (data.result && data.result.function_results && data.result.function_results.length > 0) {
            // Check if any of the function results were successful operations that modify data
            const hasDataModifyingOperations = data.result.function_results.some(result => 
              result.function !== 'search_leads' && result.result && result.result.success
            );
            
            if (hasDataModifyingOperations && onLeadsUpdated) {
              onLeadsUpdated();
            }
          }
        } else if (data.state === 'FAILURE') {
          clearInterval(pollingIntervalRef.current);
          setIsLoading(false);
          setCurrentTaskId(null);

          // Add error message
          setMessages(prev => [...prev, {
            id: Date.now(),
            message: 'I apologize, but I encountered an error processing your request. Please try again.',
            isUser: false,
            timestamp: new Date().toISOString()
          }]);
        }
        // Continue polling for PENDING and PROCESSING states
      } catch (error) {
        console.error('Error polling task status:', error);
        clearInterval(pollingIntervalRef.current);
        setIsLoading(false);
        setCurrentTaskId(null);

        setMessages(prev => [...prev, {
          id: Date.now(),
          message: 'Connection error. Please check your internet connection and try again.',
          isUser: false,
          timestamp: new Date().toISOString()
        }]);
      }
    }, 2000); // Poll every 2 seconds
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      message: inputValue.trim(),
      isUser: true,
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send message to backend
      const response = await fetch(`${API_BASE_URL}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include session cookies
        body: JSON.stringify({
          message: userMessage.message
        })
      });

      const data = await response.json();

      if (response.ok && data.task_id) {
        setCurrentTaskId(data.task_id);
        // Start polling for task completion
        pollTaskStatus(data.task_id);
      } else {
        throw new Error(data.error || 'Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setIsLoading(false);

      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        message: 'Failed to send message. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString()
      }]);
    }
  };

  const clearConversation = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/clear/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (response.ok) {
        setMessages([]);
        // Stop any ongoing polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        setIsLoading(false);
        setCurrentTaskId(null);
      }
    } catch (error) {
      console.error('Error clearing conversation:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const handleConfirmAction = (confirmationMessage) => {
    // Send the confirmation message as if the user typed it
    const userMessage = {
      id: Date.now(),
      message: confirmationMessage,
      isUser: true,
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Send to backend
    fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        message: confirmationMessage
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.task_id) {
        setCurrentTaskId(data.task_id);
        pollTaskStatus(data.task_id);
      } else {
        throw new Error(data.error || 'Failed to send confirmation');
      }
    })
    .catch(error => {
      console.error('Error sending confirmation:', error);
      setIsLoading(false);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        message: 'Failed to send confirmation. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString()
      }]);
    });
  };

  return (
    <div className="chat-widget">
      <ChatButton 
        isOpen={isOpen} 
        onClick={toggleChat}
        hasUnreadMessages={false}
      />
      
      {isOpen && (
        <div className="chat-interface">
          <div className="chat-header">
            <h3>CRM Assistant</h3>
            <button 
              className="clear-button"
              onClick={clearConversation}
              title="Clear conversation"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3,6 5,6 21,6"></polyline>
                <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2"></path>
              </svg>
            </button>
          </div>
          
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <p>Hello! I'm your CRM assistant. I can help you:</p>
                <ul>
                  <li>Update lead statuses</li>
                  <li>Modify lead information</li>
                  <li>Create new leads</li>
                  <li>Search for leads</li>
                  <li>Delete leads</li>
                </ul>
                <p>Just tell me what you'd like to do!</p>
              </div>
            )}
            
            {messages.map((msg) => (
              <ChatMessage
                key={msg.id}
                message={msg.message}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
                isConfirmationRequest={msg.isConfirmationRequest}
                functionResults={msg.functionResults}
                onConfirmAction={handleConfirmAction}
              />
            ))}
            
            {isLoading && (
              <ChatMessage isLoading={true} />
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          <div className="chat-input">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading}
              rows={1}
            />
            <button 
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="send-button"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22,2 15,22 11,13 2,9 22,2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget; 