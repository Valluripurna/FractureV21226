import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { jsPDF } from 'jspdf';
import Login from './components/Login';
import Signup from './components/Signup';
import History from './components/History';
import './App.css';

// Import icons
import { FiUploadCloud, FiAlertTriangle, FiCheckCircle, FiMessageSquare, FiDownload, FiLogOut, FiUser, FiX, FiSend, FiFileText, FiPlus, FiHeart, FiClock, FiActivity, FiMapPin, FiSearch } from 'react-icons/fi';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('login');
  const [isDragging, setIsDragging] = useState(false);
  const [nearbyHospitals, setNearbyHospitals] = useState([]);
  const [showHospitalsModal, setShowHospitalsModal] = useState(false);
  const [showLocationPermissionModal, setShowLocationPermissionModal] = useState(false);
  const fileInputRef = useRef(null);
  const chatMessagesRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('Checking for token:', token);
    if (token) {
      axios.get('http://localhost:5000/user-details', {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(response => {
        console.log('User details response:', response.data);
        setUser(response.data.user);
        setCurrentView('app');
      })
      .catch(() => {
        console.log('Token invalid, removing and redirecting to login');
        localStorage.removeItem('token');
        setCurrentView('login');
      });
    }
  }, []);

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '');
      console.log('Hash changed to:', hash);
      if (['signup', 'login', 'history', 'app'].includes(hash)) {
        setCurrentView(hash);
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    handleHashChange();
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleLoginSuccess = (userData) => {
    console.log('Login successful, setting user data:', userData);
    setUser(userData);
    setCurrentView('app');
    window.location.hash = '';
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setResult(null);
    setFile(null);
    setPreview(null);
    setCurrentView('login');
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      processFile(selectedFile);
    }
  };

  const processFile = (file) => {
    setFile(file);
    setResult(null);
    setError('');
    setShowChat(false);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      processFile(droppedFile);
    } else {
      setError('Please upload an image file (JPEG, PNG, BMP, TIFF)');
    }
  };

  const handleUploadAnother = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError('');
    setShowChat(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDownloadPDF = () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    const genAt = new Date();
    const reportId = `FD-${genAt.getHours()}${genAt.getMinutes()}${genAt.getSeconds()}${genAt.getMilliseconds()}`;
    doc.setProperties({ title: 'FractureDetect AI Report' });

    // Color palette and helpers
    const colors = {
      header: [41, 128, 185],
      patient: [34, 197, 94],
      results: [59, 130, 246],
      recs: [244, 114, 182],
      hospitals: [99, 102, 241],
      disclaimer: [100, 100, 100],
    };
    const sectionBar = (title, color, yPos) => {
      doc.setFillColor(color[0], color[1], color[2]);
      doc.rect(0, yPos, 210, 10, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(14);
      doc.text(title, 12, yPos + 7);
      doc.setTextColor(0, 0, 0);
      return yPos + 14;
    };

    // Page 1 Header
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]);
    doc.rect(0, 0, 210, 18, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(16);
    doc.text('FractureDetect AI', 12, 12);
    doc.setFontSize(10);
    doc.text('Advanced Bone Fracture Detection System', 150, 12, { align: 'center', maxWidth: 80 });

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(9);
    doc.text(`Report Generated: ${genAt.toLocaleDateString()} ${genAt.toLocaleTimeString()}   Report ID: ${reportId}`, 12, 24);

    // Patient Info
    let y = sectionBar('Patient Information', colors.patient, 30);
    doc.setFontSize(11);
    doc.text(`Name: ${user?.name || 'N/A'}`, 14, y); y += 6;
    doc.text(`Email: ${user?.email || 'N/A'}`, 14, y); y += 6;
    if (user?.phone) { doc.text(`Phone: ${user.phone}`, 14, y); y += 6; }
    if (user?.age) { doc.text(`Age: ${user.age}`, 14, y); y += 8; }

    // Detection Results
    y = sectionBar('Detection Results', colors.results, y);
    doc.setFontSize(11);
    if (result.fracture_detected) { doc.setTextColor(220, 38, 38); } else { doc.setTextColor(34, 197, 94); }
    doc.text(`Fracture Status: ${result.fracture_detected ? 'FRACTURE DETECTED' : 'NO FRACTURE DETECTED'}`, 14, y); y += 6;
    doc.setTextColor(0,0,0);
    doc.text(`Confidence: ${(result.confidence * 100).toFixed(1)}%`, 14, y); y += 6;
    doc.text(`Region: ${result.body_region || 'N/A'}`, 14, y); y += 6;
    doc.text(`Model: ${result.model_version || 'Unknown'}`, 14, y); y += 6;
    doc.text(`Model Accuracy: ${result.model_accuracy || 'N/A'}`, 14, y); y += 8;

    // X-ray image
    if (preview) {
      try {
        doc.setFontSize(12);
        doc.text('X-ray Analysis Image', 12, y);
        const imgY = y + 4;
        const imgW = 180; // keep aspect with height
        const imgH = 100;
        doc.addImage(preview, 'JPEG', 12, imgY, imgW, imgH);
        y = imgY + imgH + 4;
      } catch (e) {
        // ignore image add errors
      }
    }
    // Footer page number
    doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 1 of 3', 105, 290, { align: 'center' });

    // Page 2: Recommendations
    doc.addPage();
    doc.setFillColor(colors.header[0], colors.header[1], colors.header[2]); doc.rect(0, 0, 210, 10, 'F');
    y = sectionBar('Medical Recommendations', colors.recs, 14);
    doc.setFontSize(12);
    doc.text('Dietary Guidelines:', 12, y); y += 5;
    const diet = [
      '• Increase Calcium: dairy, leafy greens, sardines',
      '• Vitamin D: fatty fish, fortified foods, sunlight',
      '• Protein: lean meats, beans, eggs, dairy',
      '• Vitamin C: citrus fruits, berries, bell peppers',
      '• Magnesium & Zinc: nuts, seeds, whole grains',
      '• Stay Hydrated: 8–10 glasses of water daily',
    ];
    diet.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;
    doc.setFontSize(12); doc.text('Treatment Recommendations:', 12, y); y += 5;
    const tx = [
      '• Follow prescribed pain medications as directed',
      '• Consider anti-inflammatory drugs when recommended',
      '• Calcium and Vitamin D supplements as advised',
      '• Physical therapy as prescribed',
      '• Adequate rest and sleep for healing',
      '• Avoid smoking and limit alcohol',
    ];
    tx.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;
    doc.setFontSize(12); doc.text('Recovery Timeline:', 12, y); y += 5;
    const timeline = [
      '• 1–2 weeks: inflammation phase',
      '• 2–6 weeks: soft callus formation',
      '• 6–12 weeks: hard callus (bone strengthening)',
      '• 6–24 months: remodeling phase',
      '• Full recovery varies by fracture type and individual',
    ];
    timeline.forEach(line => { doc.text(line, 16, y); y += 5; });
    y += 4;
    doc.setFontSize(12); doc.text('Exercise Guidelines:', 12, y); y += 5;
    const ex = [
      '• Follow doctor-approved activity restrictions',
      '• Isometric exercises during immobilization',
      '• Gradual return to weight-bearing activities',
      '• Supervised physical therapy for mobility/strength',
      '• Avoid high-impact activities until cleared',
    ];
    ex.forEach(line => { doc.text(line, 16, y); y += 5; });
    doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 2 of 3', 105, 290, { align: 'center' });

    // Page 3: Nearby Hospitals + Disclaimer
    doc.addPage();
    doc.setFillColor(41, 128, 185); doc.rect(0, 0, 210, 10, 'F');
    doc.setTextColor(0,0,0); y = 18;
    y = sectionBar('Nearby Hospitals', colors.hospitals, 14);
    const hosps = nearbyHospitals && nearbyHospitals.length ? nearbyHospitals : [
      { name: 'City General Hospital', address: '123 Main Street, City Center', distance_km: 2.5, specialties: ['Orthopedics','Emergency Medicine'] },
      { name: 'Metropolitan Medical Center', address: '456 Oak Avenue, Downtown', distance_km: 4.2, specialties: ['Orthopedic Surgery','Sports Medicine'] },
      { name: 'University Orthopedic Clinic', address: '789 Pine Road, University District', distance_km: 6.8, specialties: ['Orthopedic Trauma','Hand Surgery'] },
      { name: 'Community Health Hospital', address: '321 Elm Street, Westside', distance_km: 7.3, specialties: ['General Medicine','Emergency Care'] },
      { name: 'Specialty Bone & Joint Center', address: '654 Cedar Boulevard, North District', distance_km: 9.1, specialties: ['Orthopedic Surgery','Spine Surgery'] },
    ];
    hosps.slice(0,5).forEach((h, idx) => {
      doc.setFontSize(12);
      doc.setTextColor(59,130,246);
      doc.text(`${idx+1}. ${h.name}`, 12, y); y += 5;
      doc.setFontSize(10);
      doc.setTextColor(0,0,0);
      doc.text(`Address: ${h.address}`, 16, y); y += 4;
      if (h.distance_km !== undefined) { doc.text(`Distance: ${h.distance_km} km`, 16, y); y += 4; }
      if (h.specialties) { doc.text(`Specialties: ${h.specialties.join(', ')}`, 16, y); y += 5; }
      y += 2;
    });
    y += 6;
    y = sectionBar('Medical Disclaimer', colors.disclaimer, y);
    doc.setFontSize(10); doc.setTextColor(100,100,100);
    doc.text('This AI analysis is for informational purposes only. Always consult with a qualified healthcare professional.', 12, y, { maxWidth: 186 });
    doc.setFontSize(9); doc.setTextColor(120,120,120); doc.text('Page 3 of 3', 105, 290, { align: 'center' });

    doc.save(`Fracture-Report-${genAt.toISOString().split('T')[0]}-${reportId}.pdf`);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('Prediction result:', response.data);
      setResult(response.data);
    } catch (err) {
      console.error('Error uploading file:', err);
      if (err.response) {
        if (err.response.status === 401) {
          alert('Session expired. Please log in again.');
          handleLogout();
        } else {
          setError(`Error: ${err.response.data.error || 'Could not process the image.'}`);
        }
      } else {
        setError('Network error. Please ensure the backend is running and accessible.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', content: chatInput };
    setChatHistory(prev => [...prev, userMsg]);
    setChatInput('');

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5000/chat', {
        message: userMsg.content,
        context: result
      }, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setChatHistory(prev => [...prev, { role: 'ai', content: response.data.response }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'ai', content: "Sorry, I couldn't get a response." }]);
    }
  };

  const requestLocationAccess = async () => {
    if (!navigator.geolocation) {
      setShowLocationPermissionModal(false);
      setNearbyHospitals([]);
      setShowHospitalsModal(true);
      return;
    }
    navigator.geolocation.getCurrentPosition(async (pos) => {
      try {
        const { latitude, longitude } = pos.coords;
        const resp = await axios.post('http://localhost:5000/nearby_hospitals', { latitude, longitude });
        if (resp.data && resp.data.hospitals) {
          setNearbyHospitals(resp.data.hospitals);
        }
      } catch (e) {
        console.error('Error getting hospitals:', e);
        setNearbyHospitals([]);
      } finally {
        setShowLocationPermissionModal(false);
        setShowHospitalsModal(true);
      }
    }, (err) => {
      console.error('Geolocation error:', err);
      setNearbyHospitals([]);
      setShowLocationPermissionModal(false);
      setShowHospitalsModal(true);
    });
  };

  const handleFindHospitals = () => {
    setShowLocationPermissionModal(true);
  };

  const renderView = () => {
    console.log('Rendering view:', currentView);
    switch (currentView) {
      case 'login':
        return <Login onLoginSuccess={handleLoginSuccess} />;
      case 'signup':
        return <Signup onSignupSuccess={() => setCurrentView('login')} onLoginSuccess={handleLoginSuccess} />;
      case 'history':
        return <History user={user} onBack={() => setCurrentView('app')} />;
      default:
        return renderApp();
    }
  };

  const renderApp = () => {
    console.log('Rendering App, user:', user, 'result:', result);
    return (
    <div className="app-container">
      <header className="header">
        <div className="logo">
          <FiFileText /> FractureDetect AI
        </div>
        {user && (
          <div className="user-info">
            <div className="user-welcome">
              <FiUser />
              <span>Welcome, {user.name}</span>
              <div className="user-status">
                <div className="status-indicator"></div>
                <span>Online</span>
              </div>
            </div>
            <nav className="navigation">
              <button className="nav-btn" onClick={() => window.location.hash = 'history'}>
                <FiFileText /> History
              </button>
              <button className="logout-btn" onClick={handleLogout}>
                <FiLogOut /> Logout
              </button>
            </nav>
          </div>
        )}
      </header>

      <main className="main-content">
        {!result ? (
          <div className="upload-section">
            <h1 className="hero-title">Upload Your X-Ray Image</h1>
            <p className="hero-subtitle">Get an instant AI-powered fracture analysis.</p>
            <div className="upload-card">
              <form onSubmit={handleSubmit}>
                <label 
                  htmlFor="file-upload" 
                  className={`upload-label ${preview ? 'has-preview' : ''} ${isDragging ? 'dragging' : ''}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                >
                  {preview ? (
                    <img src={preview} alt="X-ray preview" className="image-preview" />
                  ) : (
                    <div className="upload-placeholder">
                      <FiUploadCloud />
                      <span>{file ? file.name : "Click or drag to upload"}</span>
                      <p>Supports JPEG, PNG, BMP, TIFF formats</p>
                    </div>
                  )}
                </label>
                <input
                  id="file-upload"
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="file-input"
                />
                <button type="submit" className="analyze-btn" disabled={!file || loading}>
                  {loading ? (
                    <>
                      <div className="spinner"></div>
                      Analyzing...
                    </>
                  ) : 'Analyze Image'}
                </button>
              </form>
              {error && <div className="error-message"><FiAlertTriangle /> {error}</div>}
            </div>
          </div>
        ) : (
          <div className="results-section">
            <h1 className="hero-title">Analysis Complete</h1>
            <div className="results-grid">
              <div className="result-card">
                <h3>Detection Result</h3>
                <div className={`status ${result.fracture_detected ? 'fracture' : 'normal'}`}>
                  {result.fracture_detected ? <FiAlertTriangle /> : <FiCheckCircle />}
                  <span>{result.fracture_detected ? 'Fracture Detected' : 'No Fracture Detected'}</span>
                </div>
                <div className="result-details">
                  <div className="detail-item">
                    <FiActivity />
                    <div>
                      <span className="detail-label">Confidence</span>
                      <span className="detail-value">{(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <FiFileText />
                    <div>
                      <span className="detail-label">Model Used</span>
                      <span className="detail-value model-name-display">{result.model_version}</span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <FiCheckCircle />
                    <div>
                      <span className="detail-label">Model Accuracy</span>
                      <span className="detail-value">{result.model_accuracy}</span>
                    </div>
                  </div>
                  <div className="detail-item">
                    <FiClock />
                    <div>
                      <span className="detail-label">Analysis Time</span>
                      <span className="detail-value">{new Date().toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
                <div className="result-actions">
                  <button onClick={handleDownloadPDF}><FiDownload /> Download Report</button>
                  <button onClick={() => setShowChat(true)}><FiMessageSquare /> Medical Assistant</button>
                  <button onClick={handleFindHospitals}><FiMapPin /> Find Hospitals</button>
                </div>
              </div>
              <div className="image-card">
                <h3>Your X-Ray</h3>
                <img src={preview} alt="X-ray" />
              </div>
            </div>
            <button className="upload-another-btn" onClick={handleUploadAnother}><FiPlus /> Upload Another</button>
          </div>
        )}
      </main>

      {showChat && (
        <div className="chat-overlay">
          <div className="chat-window">
            <div className="chat-header">
              <h3>Medical Assistant</h3>
              <button onClick={() => setShowChat(false)}><FiX /></button>
            </div>
            <div className="chat-messages" ref={chatMessagesRef}>
              <div className="chat-intro">
                <FiHeart />
                <p>Hello! I'm your AI medical assistant. How can I help you with your fracture analysis?</p>
              </div>
              {chatHistory.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  {msg.content}
                </div>
              ))}
            </div>
            <form className="chat-input-form" onSubmit={handleChatSubmit}>
              <input
                type="text"
                placeholder="Ask a question..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit"><FiSend /></button>
            </form>
          </div>
        </div>
      )}

      {showLocationPermissionModal && (
        <div className="location-overlay" onClick={() => setShowLocationPermissionModal(false)}>
          <div className="location-window" onClick={(e) => e.stopPropagation()}>
            <div className="location-header">
              <h3><FiMapPin /> Location Permission</h3>
              <button className="close-btn" onClick={() => setShowLocationPermissionModal(false)}><FiX /></button>
            </div>
            <div className="location-body">
              <p>We use your location to list nearby hospitals for faster clinical access. Please allow location access.</p>
              <div className="location-actions">
                <button className="nav-btn" onClick={requestLocationAccess}><FiMapPin /> Allow Location Access</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showHospitalsModal && (
        <div className="hospitals-overlay" onClick={() => setShowHospitalsModal(false)}>
          <div className="hospitals-window" onClick={(e) => e.stopPropagation()}>
            <div className="hospitals-header">
              <h3><FiMapPin /> Nearby Hospitals</h3>
              <button className="close-btn" onClick={() => setShowHospitalsModal(false)}><FiX /></button>
            </div>
            <div className="hospitals-list">
              {(nearbyHospitals && nearbyHospitals.length ? nearbyHospitals : [
                { name: 'City General Hospital', address: '123 Main Street, City Center', distance_km: 2.5, specialties: ['Orthopedics','Emergency Medicine'] },
                { name: 'Metropolitan Medical Center', address: '456 Oak Avenue, Downtown', distance_km: 4.2, specialties: ['Orthopedic Surgery','Sports Medicine'] },
                { name: 'University Orthopedic Clinic', address: '789 Pine Road, University District', distance_km: 6.8, specialties: ['Orthopedic Trauma','Hand Surgery'] },
                { name: 'Community Health Hospital', address: '321 Elm Street, Westside', distance_km: 7.3, specialties: ['General Medicine','Emergency Care'] },
                { name: 'Specialty Bone & Joint Center', address: '654 Cedar Boulevard, North District', distance_km: 9.1, specialties: ['Orthopedic Surgery','Spine Surgery'] },
              ]).slice(0,5).map((h, idx) => (
                <div className="hospital-item" key={idx}>
                  <div className="hospital-icon"><FiSearch /></div>
                  <div className="hospital-info">
                    <div className="hospital-name">{h.name}</div>
                    <div className="hospital-meta">{h.address}</div>
                    {h.distance_km !== undefined && (
                      <div className="hospital-meta">Distance: {h.distance_km} km</div>
                    )}
                    {h.specialties && (
                      <div className="hospital-meta">Specialties: {h.specialties.join(', ')}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
  };

  return renderView();
}

export default App;
