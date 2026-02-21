import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './History.css';

const History = ({ user }) => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUserReports();
  }, []);

  const fetchUserReports = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:5000/user-reports', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(response.data.reports);
    } catch (err) {
      setError('Failed to fetch reports');
      console.error('Error fetching reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getStatusBadge = (isFracture) => {
    return (
      <span className={`status-badge ${isFracture ? 'fracture' : 'normal'}`}>
        {isFracture ? 'Fracture Detected' : 'No Fracture'}
      </span>
    );
  };

  if (loading) {
    return <div className="history-container"><div className="loading">Loading reports...</div></div>;
  }

  if (error) {
    return <div className="history-container"><div className="error-message">{error}</div></div>;
  }

  return (
    <div className="history-container">
      <h2>My Reports</h2>
      <p className="subtitle">View your previous fracture detection reports</p>
      
      {reports.length === 0 ? (
        <div className="no-reports">
          <p>You haven't generated any reports yet.</p>
          <p>Upload an X-ray image to get started!</p>
        </div>
      ) : (
        <div className="reports-list">
          {reports.map((report) => (
            <div key={report._id} className="report-card">
              <div className="report-header">
                <h3>Fracture Detection Report</h3>
                <span className="report-date">{formatDate(report.created_at)}</span>
              </div>
              
              <div className="report-body">
                <div className="report-field">
                  <span className="field-label">Status:</span>
                  {getStatusBadge(report.report_data.fracture_detected)}
                </div>
                
                <div className="report-field">
                  <span className="field-label">Confidence:</span>
                  <span className="field-value">{(report.report_data.confidence * 100).toFixed(1)}%</span>
                </div>
                
                <div className="report-field">
                  <span className="field-label">Body Region:</span>
                  <span className="field-value">{report.report_data.body_region}</span>
                </div>
                
                <div className="report-field">
                  <span className="field-label">Model Used:</span>
                  <span className="field-value model-name">{report.report_data.model_version}</span>
                </div>
                
                {report.image_id && (
                  <div className="report-field">
                    <span className="field-label">Image:</span>
                    <img 
                      src={`http://localhost:5000/report-image/${report.image_id}`} 
                      alt="X-ray" 
                      className="report-image"
                    />
                  </div>
                )}
              </div>
              
              <div className="report-footer">
                <button 
                  className="view-report-btn"
                  onClick={() => window.open(`http://localhost:5000/report/${report._id}`, '_blank')}
                >
                  View Full Report
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;