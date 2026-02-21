import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

const Login = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showOTP, setShowOTP] = useState(false);
  const [otp, setOtp] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/login', {
        email,
        password
      });
      
      localStorage.setItem('token', response.data.access_token);
      onLoginSuccess(response.data.user);
    } catch (err) {
      if (err.response) {
        const msg = err.response.data && err.response.data.error ? err.response.data.error : '';
        if (err.response.status === 401 && msg === 'User not found') {
          setError('No account found. Please sign up.');
        } else if (err.response.status === 401) {
          setError('Invalid email or password');
        } else {
          setError(msg || 'An error occurred. Please try again.');
        }
      } else {
        setError('Network error. Please ensure the backend is running.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendOTP = async () => {
    if (!email) {
      setError('Please enter your email first');
      return;
    }
    
    setIsLoading(true);
    setError('');
    
    try {
      const resp = await axios.post('http://localhost:5000/send-otp', { email });
      setShowOTP(true);
      // In development, backend may return dev_otp for testing
      if (resp.data && resp.data.dev_otp) {
        setOtp(resp.data.dev_otp);
      }
    } catch (err) {
      setError('Failed to send OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post('http://localhost:5000/verify-otp', {
        email,
        otp
      });
      
      localStorage.setItem('token', response.data.access_token);
      onLoginSuccess(response.data.user);
    } catch (err) {
      setError('Invalid OTP. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Login to FractureDetect</h2>
          <p>Access your fracture detection reports</p>
        </div>
        
        {!showOTP ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="Enter your email"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="Enter your password"
              />
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button type="submit" className="auth-btn" disabled={isLoading}>
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
            
            <div className="auth-divider">
              <span>or</span>
            </div>
            
            <button 
              type="button" 
              className="otp-btn" 
              onClick={handleSendOTP}
              disabled={isLoading}
            >
              {isLoading ? 'Sending OTP...' : 'Login with OTP'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOTP}>
            <div className="form-group">
              <label htmlFor="otp">Enter OTP</label>
              <input
                type="text"
                id="otp"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
                placeholder="Enter 6-digit OTP"
                maxLength="6"
              />
              <p className="otp-info">OTP sent to {email}{otp ? ` • Use OTP: ${otp}` : ''}</p>
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button type="submit" className="auth-btn" disabled={isLoading}>
              {isLoading ? 'Verifying...' : 'Verify OTP'}
            </button>
            
            <button 
              type="button" 
              className="resend-otp-btn" 
              onClick={handleSendOTP}
              disabled={isLoading}
            >
              Resend OTP
            </button>
          </form>
        )}
        
        <div className="auth-footer">
          <p>Don't have an account? <button className="link-btn" onClick={() => window.location.hash = 'signup'}>Sign Up</button></p>
        </div>
      </div>
    </div>
  );
};

export default Login;