import React, { useState, useEffect, useRef } from 'react';
import ChatButton from './ChatButton';
import ChatMessage from './ChatMessage';
import ConversationList from './ConversationList';
import './ChatWidget.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatWidget = ({ onLeadsUpdated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [conversationRefresh, setConversationRefresh] = useState(0);
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
        const response = await fetch(`${API_BASE_URL}/chat/status/${taskId}/`, {
          credentials: 'include', // Include session cookies for authentication
        });
        const data = await response.json();

        if (data.state === 'SUCCESS') {
          clearInterval(pollingIntervalRef.current);
          setIsLoading(false);

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
          message: userMessage.message,
          conversation_id: currentConversationId
        })
      });

      const data = await response.json();

      if (response.ok && data.task_id) {
        // Update conversation ID if returned
        if (data.conversation_id && data.conversation_id !== currentConversationId) {
          setCurrentConversationId(data.conversation_id);
          // Trigger conversation list refresh
          setConversationRefresh(prev => prev + 1);
        }
        
        // If this is the first message in a "New Chat" conversation, update the title
        if (currentConversationId && data.conversation_id === currentConversationId) {
          // Check if we need to update the conversation title
          // This will be handled by the backend when it creates the conversation title
          setConversationRefresh(prev => prev + 1);
        }
        
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

  // Load messages for a specific conversation
  const loadConversationMessages = async (conversationId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages/`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const messages = await response.json();
        // Transform backend messages to frontend format
        const formattedMessages = messages.map(msg => ({
          id: msg.id,
          message: msg.content,
          isUser: msg.role === 'user',
          timestamp: msg.created_at,
          isConfirmationRequest: false,
          functionResults: msg.function_results ? JSON.parse(msg.function_results) : null
        }));
        setMessages(formattedMessages);
      } else {
        console.error('Failed to load conversation messages');
      }
    } catch (error) {
      console.error('Error loading conversation messages:', error);
    }
  };

  // Handle conversation selection
  const handleSelectConversation = (conversationId) => {
    if (conversationId === currentConversationId) return;
    
    setCurrentConversationId(conversationId);
    if (conversationId) {
      loadConversationMessages(conversationId);
    } else {
      setMessages([]);
    }
    
    // Stop any ongoing polling when switching conversations
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }
    setIsLoading(false);
  };

  // Handle new conversation - create empty conversation like ChatGPT
  const handleNewConversation = async () => {
    try {
      // Create a new empty conversation
      const response = await fetch(`${API_BASE_URL}/conversations/create/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          title: 'New Chat' // Temporary title, will be updated with first message
        })
      });

      if (response.ok) {
        const newConversation = await response.json();
        
        // Switch to the new conversation
        setCurrentConversationId(newConversation.id);
        setMessages([]);
        
        // Stop any ongoing polling
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        setIsLoading(false);
        
        // Refresh conversation list to show the new conversation
        setConversationRefresh(prev => prev + 1);
      } else {
        console.error('Failed to create new conversation');
        // Fallback to old behavior
        setCurrentConversationId(null);
        setMessages([]);
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
        }
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error creating new conversation:', error);
      // Fallback to old behavior
      setCurrentConversationId(null);
      setMessages([]);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      setIsLoading(false);
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
    if (!isOpen) {
      setIsCollapsed(false);
    }
  };

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
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
        message: confirmationMessage,
        conversation_id: currentConversationId
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.task_id) {
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
      {/* Show chat button when closed OR when collapsed */}
      {(!isOpen || isCollapsed) && (
        <ChatButton 
          isOpen={false} // Always show as closed state (blue bubble)
          onClick={isCollapsed ? toggleCollapse : toggleChat}
          hasUnreadMessages={false}
        />
      )}
      
      {/* Only show red X button when chat is open AND not collapsed */}
      {isOpen && !isCollapsed && (
        <ChatButton 
          isOpen={true} // Show as open state (red X button)
          onClick={toggleChat}
          hasUnreadMessages={false}
        />
      )}
      
      {isOpen && !isCollapsed && (
        <div className={`chat-interface ${showSidebar ? 'with-sidebar' : ''}`}>
          <div className="chat-header">
            <h3>CRM Assistant</h3>
            <div className="header-controls">
              <button 
                className="new-chat-button"
                onClick={handleNewConversation}
                title="Start new conversation"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2v20M2 12h20"></path>
                </svg>
              </button>
              <button 
                className="sidebar-toggle-button"
                onClick={() => setShowSidebar(!showSidebar)}
                title={showSidebar ? "Hide conversations" : "Show conversations"}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="9" y1="9" x2="15" y2="9"></line>
                  <line x1="9" y1="12" x2="15" y2="12"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                </svg>
              </button>
              <button 
                className="minimize-button"
                onClick={toggleCollapse}
                title="Minimize chat"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
              </button>
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
          </div>
          
          <div className="chat-content">
            {showSidebar && (
              <div className="chat-sidebar">
                <ConversationList
                  selectedConversationId={currentConversationId}
                  onSelectConversation={handleSelectConversation}
                  onNewConversation={handleNewConversation}
                  refreshTrigger={conversationRefresh}
                />
              </div>
            )}
            
            <div className="chat-main">
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
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatWidget; 