import React, { useState } from 'react';
import './LeadForm.css';

const LeadForm = ({ onSubmit, onCancel, defaultStatus = 'Interest' }) => {
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    email: '',
    phone: '',
    value: '',
    notes: '',
    status: defaultStatus,
    source: ''
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState({});

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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
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
    
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (formData.value && isNaN(parseFloat(formData.value))) {
      newErrors.value = 'Value must be a number';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const submitData = {
        ...formData,
        value: formData.value ? parseFloat(formData.value) : null
      };
      
      await onSubmit(submitData);
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getStatusDisplayName = (status) => {
    switch (status) {
      case 'Meeting booked':
        return 'Meeting Booked';
      case 'Proposal sent':
        return 'Proposal Sent';
      case 'Closed win':
        return 'Closed Win';
      case 'Closed lost':
        return 'Closed Lost';
      default:
        return status;
    }
  };

  return (
    <div className="lead-form-overlay">
      <div className="lead-form-container">
        <div className="lead-form-header">
          <h2>Add New Lead to {getStatusDisplayName(defaultStatus)}</h2>
          <button 
            className="close-btn"
            onClick={onCancel}
            type="button"
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="lead-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className={errors.name ? 'error' : ''}
                placeholder="Enter lead name"
              />
              {errors.name && <span className="error-text">{errors.name}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="company">Company</label>
              <input
                type="text"
                id="company"
                name="company"
                value={formData.company}
                onChange={handleChange}
                placeholder="Enter company name"
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? 'error' : ''}
                placeholder="Enter email address"
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="Enter phone number"
              />
            </div>
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="value">Deal Value ($)</label>
              <input
                type="number"
                id="value"
                name="value"
                value={formData.value}
                onChange={handleChange}
                className={errors.value ? 'error' : ''}
                placeholder="0.00"
                step="0.01"
                min="0"
              />
              {errors.value && <span className="error-text">{errors.value}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                name="status"
                value={formData.status}
                onChange={handleChange}
              >
                {statusOptions.map(status => (
                  <option key={status} value={status}>
                    {getStatusDisplayName(status)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="source">Source</label>
            <select
              id="source"
              name="source"
              value={formData.source}
              onChange={handleChange}
            >
              <option value="">Select source...</option>
              {sourceOptions.map(source => (
                <option key={source} value={source}>
                  {source}
                </option>
              ))}
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="notes">Notes</label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Enter any additional notes..."
              rows="3"
            />
          </div>
          
          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Adding...' : 'Add Lead'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LeadForm; 