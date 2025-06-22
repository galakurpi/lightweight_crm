import React, { useState } from 'react';
import './LeadDetailsModal.css';

const LeadDetailsModal = ({ lead, onClose, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    name: lead?.name || '',
    company: lead?.company || '',
    email: lead?.email || '',
    phone: lead?.phone || '',
    value: lead?.value || '',
    notes: lead?.notes || '',
    status: lead?.status || 'Interest',
    source: lead?.source || ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

  if (!lead) return null;

  const statusOptions = [
    'Interest',
    'Meeting booked',
    'Proposal sent',
    'Closed win',
    'Closed lost'
  ];

  const sourceOptions = [
    'Website',
    'Referral',
    'Social Media',
    'Cold Call',
    'Email Campaign',
    'Trade Show',
    'Other'
  ];

  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'No value';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getInitials = (name) => {
    if (!name) return '?';
    return name
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleEditToggle = () => {
    if (isEditing) {
      // Reset form data to original values when canceling edit
      setEditData({
        name: lead.name || '',
        company: lead.company || '',
        email: lead.email || '',
        phone: lead.phone || '',
        value: lead.value || '',
        notes: lead.notes || '',
        status: lead.status || 'Interest',
        source: lead.source || ''
      });
      setErrors({});
    }
    setIsEditing(!isEditing);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!editData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!editData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(editData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (editData.value && isNaN(parseFloat(editData.value))) {
      newErrors.value = 'Value must be a number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const updateData = {
        ...editData,
        value: editData.value ? parseFloat(editData.value) : null
      };
      
      await onUpdate(lead.id, updateData);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating lead:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderEditableField = (label, name, value, type = 'text', options = null) => {
    if (isEditing) {
      if (options) {
        // Render select dropdown
        return (
          <div className="detail-item">
            <span className="detail-label">{label}:</span>
            <select
              name={name}
              value={editData[name]}
              onChange={handleInputChange}
              className={`detail-input ${errors[name] ? 'error' : ''}`}
            >
              {name === 'source' && <option value="">Select source...</option>}
              {options.map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
            {errors[name] && <span className="error-text">{errors[name]}</span>}
          </div>
        );
      } else {
        // Render input field
        return (
          <div className="detail-item">
            <span className="detail-label">{label}:</span>
            <input
              type={type}
              name={name}
              value={editData[name]}
              onChange={handleInputChange}
              className={`detail-input ${errors[name] ? 'error' : ''}`}
              placeholder={`Enter ${label.toLowerCase()}`}
              step={type === 'number' ? '0.01' : undefined}
              min={type === 'number' ? '0' : undefined}
            />
            {errors[name] && <span className="error-text">{errors[name]}</span>}
          </div>
        );
      }
    } else {
      // Render read-only value
      return (
        <div className="detail-item">
          <span className="detail-label">{label}:</span>
          <span className="detail-value">{value || `No ${label.toLowerCase()} provided`}</span>
        </div>
      );
    }
  };

  const renderEditableNotes = () => {
    if (isEditing) {
      return (
        <div className="details-section">
          <h3>Notes</h3>
          <textarea
            name="notes"
            value={editData.notes}
            onChange={handleInputChange}
            className="notes-textarea"
            placeholder="Enter any additional notes..."
            rows="4"
          />
        </div>
      );
    } else if (lead.notes) {
      return (
        <div className="details-section">
          <h3>Notes</h3>
          <div className="notes-content">
            <p>{lead.notes}</p>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="lead-details-overlay">
      <div className="lead-details-container">
        <div className="lead-details-header">
          <div className="lead-details-title">
            <div className="lead-avatar-large">
              {getInitials(isEditing ? editData.name : lead.name)}
            </div>
            <div>
              <h2>{isEditing ? editData.name || 'Unnamed Lead' : lead.name || 'Unnamed Lead'}</h2>
              <p className="lead-company-subtitle">{isEditing ? editData.company || 'No company' : lead.company || 'No company'}</p>
            </div>
          </div>
          <div className="header-actions">
            <button 
              className={`btn ${isEditing ? 'btn-secondary' : 'btn-edit'}`}
              onClick={handleEditToggle}
              disabled={isSubmitting}
              type="button"
            >
              {isEditing ? '✕ Cancel' : '✏️ Edit'}
            </button>
            <button 
              className="close-btn"
              onClick={onClose}
              type="button"
            >
              ×
            </button>
          </div>
        </div>
        
        <div className="lead-details-content">
          <div className="details-section">
            <h3>Contact Information</h3>
            <div className="details-grid">
              {renderEditableField('📧 Email', 'email', lead.email, 'email')}
              {renderEditableField('📞 Phone', 'phone', lead.phone, 'tel')}
            </div>
          </div>

          <div className="details-section">
            <h3>Lead Information</h3>
            <div className="details-grid">
              {renderEditableField('👤 Name', 'name', lead.name)}
              {renderEditableField('🏢 Company', 'company', lead.company)}
            </div>
          </div>

          <div className="details-section">
            <h3>Deal Information</h3>
            <div className="details-grid">
              {renderEditableField('💰 Value', 'value', isEditing ? editData.value : formatCurrency(lead.value), 'number')}
              {renderEditableField('📊 Status', 'status', lead.status, 'text', statusOptions)}
              {renderEditableField('📍 Source', 'source', lead.source, 'text', sourceOptions)}
              <div className="detail-item">
                <span className="detail-label">#️⃣ ID:</span>
                <span className="detail-value">{lead.id}</span>
              </div>
            </div>
          </div>

          {renderEditableNotes()}

          <div className="details-section">
            <h3>Timeline</h3>
            <div className="details-grid">
              <div className="detail-item">
                <span className="detail-label">📅 Created:</span>
                <span className="detail-value">{formatDate(lead.created_at)}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">🔄 Updated:</span>
                <span className="detail-value">{formatDate(lead.updated_at)}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lead-details-footer">
          {isEditing ? (
            <div className="edit-actions">
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handleEditToggle}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button 
                type="button" 
                className="btn btn-primary"
                onClick={handleSave}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          ) : (
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default LeadDetailsModal; 