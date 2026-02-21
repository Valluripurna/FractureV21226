# FractureDetect AI - Bone Fracture Detection System

An advanced AI-powered system for detecting bone fractures in X-ray images using deep learning models.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Overview

FractureDetect AI is a comprehensive medical imaging solution that leverages multiple deep learning models to accurately detect bone fractures in X-ray images. The system provides instant analysis with confidence scoring, medical recommendations, and detailed reporting capabilities.

## Features

### Core Functionality
- **Multi-Model Detection**: Utilizes 5 different deep learning models for accurate fracture detection
- **Real-time Analysis**: Instant fracture detection with confidence scoring
- **Medical Reporting**: Comprehensive PDF reports with patient information and medical recommendations
- **Authentication System**: Secure user signup/login with JWT tokens and OTP email verification

### Advanced Features
- **Data Persistence**: MongoDB integration for storing user data, reports, and X-ray images
- **Report History**: Complete history of all fracture detection reports
- **Image Storage**: Permanent storage of uploaded X-ray images
- **Medical Assistant**: AI-powered chat for fracture care guidance
- **Hospital Finder**: Location-based hospital recommendations

### User Experience
- **Responsive Design**: Works on desktop and mobile devices
- **Intuitive Interface**: Clean, medical-themed UI with dark mode
- **Progressive Loading**: Smooth user experience with loading indicators
- **Error Handling**: Comprehensive error messaging and recovery

## Technology Stack

### Backend
- **Python 3.9+**
- **Flask**: Web framework for REST API
- **PyTorch**: Deep learning framework
- **MongoDB**: Database for user data and image storage
- **GridFS**: Large file storage for X-ray images
- **JWT**: Token-based authentication
- **SMTP**: Email service for OTP verification

### Frontend
- **React.js**: JavaScript library for UI
- **Axios**: HTTP client for API requests
- **jsPDF**: Client-side PDF generation
- **CSS3**: Styling and responsive design

### Deep Learning Models
- **ResNet50**: Convolutional neural network
- **DenseNet**: Densely connected convolutional network
- **EfficientNet**: Efficient scaling of convolutional networks
- **FracNet**: Specialized fracture detection model
- **MURA**: Musculoskeletal Radiographs model

## System Architecture

```mermaid
graph TD
    A[User Interface] --> B[React Frontend]
    B --> C[Flask Backend API]
    C --> D[MongoDB Database]
    C --> E[Deep Learning Models]
    C --> F[Email Service]
    D --> G[User Collection]
    D --> H[Reports Collection]
    D --> I[Images GridFS]
    E --> J[Model Evaluation]
    J --> K[Best Model Selection]
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 14+
- MongoDB Atlas account or local MongoDB instance
- Gmail account for SMTP (or other email service)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Required packages:
```bash
pip install torch torchvision
pip install flask flask-cors flask-jwt-extended
pip install pymongo python-dotenv
pip install pillow numpy
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node dependencies:
```bash
npm install
```

3. Required packages:
```bash
npm install axios jspdf
```

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Email Configuration
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password
SMTP_SERVER=smtp.gmail.com

# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
```

### Model Files

Place the following model files in the `models` directory:
- `resnet50_fracture_model.pth`
- `densenet121_fracture_model.pth`
- `efficientnet_fracture_model.pth`
- `fracnet_model.pth`
- `mura_model_pytorch.pth`

## Usage

### Starting the Application

1. Start the backend server:
```bash
cd backend
python app.py
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Open your browser to `http://localhost:3000`

### User Workflow

1. **Authentication**
   - Sign up for a new account or log in with existing credentials
   - Alternative OTP login via email verification

2. **Fracture Detection**
   - Upload an X-ray image (JPEG, PNG, BMP, TIFF formats supported)
   - Wait for AI analysis (typically 5-15 seconds)
   - View results with confidence scoring

3. **Report Generation**
   - Download PDF reports with patient information
   - Access medical recommendations and dietary guidelines
   - View treatment procedures based on detection results

4. **History Management**
   - View all previous reports in the History section
   - Access stored X-ray images
   - Review past detection results

## API Endpoints

### Authentication
- `POST /signup` - User registration
- `POST /login` - User authentication
- `POST /send-otp` - Send OTP to email
- `POST /verify-otp` - Verify OTP for login
- `GET /user-details` - Get authenticated user information

### Detection
- `POST /predict` - Analyze X-ray image for fractures
- `POST /chat` - Medical assistant chat
- `POST /find_hospitals` - Find nearby hospitals

### Reports
- `GET /user-reports` - Get all reports for authenticated user
- `GET /report/:id` - Get specific report by ID
- `GET /report-image/:id` - Get X-ray image by ID

### System
- `GET /health` - System health check
- `GET /model_status` - Loaded model status

## Database Schema

### Users Collection
```javascript
{
  "_id": ObjectId,
  "name": String,
  "email": String,
  "password": String, // Hashed
  "phone": String,
  "age": String,
  "created_at": Date
}
```

### Reports Collection
```javascript
{
  "_id": ObjectId,
  "user_email": String,
  "report_data": Object,
  "image_id": ObjectId, // Reference to GridFS
  "created_at": Date
}
```

### Images (GridFS)
- Files stored in MongoDB GridFS
- Metadata includes filename and upload date
- Associated with reports via image_id

## Development

### Project Structure
```
Fracture/
├── backend/
│   ├── app.py          # Main Flask application
│   ├── auth.py         # Authentication logic
│   ├── database.py     # MongoDB integration
│   ├── model.py        # Model loading and prediction
│   ├── background_evaluator.py  # Model evaluation
│   ├── .env           # Environment variables
│   └── models/        # Deep learning models
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Login.js
    │   │   ├── Signup.js
    │   │   ├── History.js
    │   │   └── Auth.css
    │   ├── App.js
    │   └── App.css
    └── public/
```

### Adding New Models

1. Place model file in `backend/models/`
2. Update `MODEL_PATHS` in `app.py`
3. Restart the backend server

### Customizing Email Templates

Modify the email template in `auth.py`:
- Update the `send_otp_email` function body
- Customize subject line and content

## Troubleshooting

### Common Issues

1. **Models Not Loading**
   - Verify model files exist in `models/` directory
   - Check file permissions
   - Ensure PyTorch is properly installed

2. **MongoDB Connection Failed**
   - Verify `MONGO_URI` in `.env` file
   - Check MongoDB Atlas IP whitelist
   - Confirm network connectivity

3. **Email OTP Not Sending**
   - Verify Gmail credentials
   - Enable 2-factor authentication and use app password
   - Check spam/junk folder

4. **Frontend Not Connecting to Backend**
   - Ensure both servers are running
   - Check CORS configuration
   - Verify API endpoints in browser console

### Error Messages

- **"Error processing image"**: Backend server may be down or model loading failed
- **"Session expired"**: JWT token has expired, log in again
- **"User already exists"**: Email already registered during signup
- **"Invalid OTP"**: OTP expired or incorrect

### Performance Optimization

1. **Model Loading**
   - Models load once at startup
   - Automatic best model selection based on evaluation

2. **Database Queries**
   - Indexed user emails for fast lookup
   - Efficient GridFS storage for images

3. **Memory Management**
   - Images cleared from memory after processing
   - Session cleanup on logout

## Security

### Authentication
- JWT tokens with 15-minute expiration
- Password hashing with SHA-256
- OTP verification for alternative login

### Data Protection
- HTTPS recommended for production
- MongoDB Atlas encryption at rest
- No sensitive data stored in frontend

### Privacy
- Patient data stored securely
- Images retained only for report history
- GDPR-compliant data handling

## Future Enhancements

### Planned Features
1. **Multi-language Support**: Localization for global users
2. **Advanced Analytics**: Trend analysis of fracture patterns
3. **Mobile App**: Native mobile application
4. **DICOM Support**: Medical imaging format compatibility
5. **Radiologist Review**: Expert verification workflow

### Model Improvements
1. **Additional Models**: Integration of newer architectures
2. **Transfer Learning**: Custom model training
3. **Ensemble Methods**: Combined model predictions
4. **Real-time Feedback**: Continuous model improvement

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is proprietary and confidential. Unauthorized copying or distribution is prohibited.

## Contact

For support or inquiries, contact the development team through the platform.