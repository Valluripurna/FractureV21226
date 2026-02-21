import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import jsonify
import json
import hashlib
from datetime import datetime, timedelta
from database import register_user, authenticate_user, get_user_details

# Simple in-memory storage for OTPs (in production, you might want to use a database)
otps = {}

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def send_otp_email(email, otp):
    """Send OTP to user's email."""
    try:
        # Get email credentials from environment variables
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        smtp_server = os.getenv('SMTP_SERVER')
        
        if not email_user or not email_pass or not smtp_server:
            return False, "Email configuration missing"
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email
        msg['Subject'] = "FractureDetect - OTP for Login/Signup"
        
        body = f"""
        Hello,
        
        Your OTP for FractureDetect is: {otp}
        
        This OTP is valid for 10 minutes.
        
        If you didn't request this OTP, please ignore this email.
        
        Best regards,
        FractureDetect Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(email_user, email_pass)
        text = msg.as_string()
        server.sendmail(email_user, email, text)
        server.quit()
        
        return True, "OTP sent successfully"
    except Exception as e:
        return False, str(e)

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_otp(email):
    """Generate and send OTP to user's email.
    In development, if email is not configured, expose the OTP in the response.
    """
    global otps
    
    # Generate OTP
    otp = generate_otp()
    
    # Store OTP with expiration time (10 minutes)
    otps[email] = {
        'otp': otp,
        'expires_at': datetime.now() + timedelta(minutes=10)
    }
    
    # Send OTP via email
    success, message = send_otp_email(email, otp)
    if success:
        # Email successfully sent; don't expose OTP
        return True, "OTP sent successfully", None
    else:
        # Development fallback: expose OTP to allow testing without email setup
        if message == "Email configuration missing":
            return True, "OTP generated (development)", otp
        # Other email errors: still expose OTP for testing
        return True, f"OTP generated (development): {message}", otp

def verify_otp(email, otp):
    """Verify OTP for a user."""
    global otps
    
    # Check if OTP exists for this email
    if email not in otps:
        return False, "OTP not found"
    
    # Check if OTP is expired
    if datetime.now() > otps[email]['expires_at']:
        del otps[email]  # Remove expired OTP
        return False, "OTP expired"
    
    # Check if OTP matches
    if otps[email]['otp'] != otp:
        return False, "Invalid OTP"
    
    # Remove used OTP
    del otps[email]
    return True, "OTP verified successfully"