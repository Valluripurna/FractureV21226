import React, { useState } from 'react';
import axios from 'axios';
import './Auth.css';

const Signup = ({ onSignupSuccess, onLoginSuccess }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [age, setAge] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      await axios.post('http://localhost:5000/signup', {
        name,
        email,
        password,
        phone,
        age
      });
      // Try to log the user in immediately after signup
      try {
        const loginResp = await axios.post('http://localhost:5000/login', { email, password });
        localStorage.setItem('token', loginResp.data.access_token);
        if (onLoginSuccess) {
          onLoginSuccess(loginResp.data.user);
          return;
        }
        setSuccess(true);
        setTimeout(() => onSignupSuccess && onSignupSuccess(), 1000);
      } catch (e) {
        // If auto-login fails, show success then send to login
        setSuccess(true);
        setTimeout(() => onSignupSuccess && onSignupSuccess(), 1500);
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>Create Account</h2>
          <p>Join FractureDetect to save your reports</p>
        </div>
        
        {success ? (
          <div className="success-message">
            <h3>Account Created Successfully!</h3>
            <p>Redirecting to login...</p>
          </div>
        ) : (
          <form onSubmit={handleSignup}>
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="Enter your full name"
              />
            </div>
            
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
                placeholder="Create a password"
                minLength="6"
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="Enter your phone number"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  placeholder="Enter your age"
                  min="1"
                  max="120"
                />
              </div>
            </div>
            
            {error && <div className="error-message">{error}</div>}
            
            <button type="submit" className="auth-btn" disabled={isLoading}>
              {isLoading ? 'Creating Account...' : 'Sign Up'}
            </button>
          </form>
        )}
        
        <div className="auth-footer">
          <p>Already have an account? <button className="link-btn" onClick={() => window.location.hash = 'login'}>Login</button></p>
        </div>
      </div>
    </div>
  );
};

export default Signup;