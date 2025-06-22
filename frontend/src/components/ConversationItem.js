import React, { useState } from 'react';

const ConversationItem = ({ 
  conversation, 
  isSelected, 
  onSelect, 
  onDelete, 
  onUpdate 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title);
  const [showMenu, setShowMenu] = useState(false);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  const handleSaveTitle = () => {
    if (editTitle.trim() && editTitle !== conversation.title) {
      onUpdate({ title: editTitle.trim() });
    }
    setIsEditing(false);
    setShowMenu(false);
  };

  const handleCancelEdit = () => {
    setEditTitle(conversation.title);
    setIsEditing(false);
    setShowMenu(false);
  };

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${conversation.title}"?`)) {
      onDelete();
    }
    setShowMenu(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSaveTitle();
    } else if (e.key === 'Escape') {
      handleCancelEdit();
    }
  };

  return (
    <div 
      className={`conversation-item ${isSelected ? 'selected' : ''}`}
      onClick={!isEditing ? onSelect : undefined}
    >
      <div className="conversation-item-content">
        {isEditing ? (
          <div className="conversation-edit">
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleKeyPress}
              onBlur={handleSaveTitle}
              autoFocus
              className="conversation-edit-input"
            />
          </div>
        ) : (
          <>
            <div className="conversation-title">
              {conversation.title}
            </div>
            <div className="conversation-date">
              {formatDate(conversation.updated_at)}
            </div>
          </>
        )}
      </div>

      {!isEditing && (
        <div className="conversation-item-actions">
          <button
            className="conversation-menu-btn"
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            title="More options"
          >
            ⋮
          </button>
          
          {showMenu && (
            <div className="conversation-menu">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                  setShowMenu(false);
                }}
                className="conversation-menu-item"
              >
                ✏️ Rename
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete();
                }}
                className="conversation-menu-item delete"
              >
                🗑️ Delete
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ConversationItem; 