# API Documentation

## Overview

This document provides detailed information about the REST API endpoints available in the FractureDetect AI system.

## Base URL

```
http://localhost:5000
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Authentication Endpoints

### User Registration
```
POST /signup
```

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "password": "string",
  "phone": "string", (optional)
  "age": "string" (optional)
}
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

**Status Codes:**
- 201: User created successfully
- 400: Validation error or user already exists
- 500: Server error

### User Login
```
POST /login
```

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Authentication successful",
  "access_token": "string",
  "user": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "age": "string",
    "_id": "string"
  }
}
```

**Status Codes:**
- 200: Login successful
- 400: Missing credentials
- 401: Invalid credentials
- 500: Server error

### Send OTP
```
POST /send-otp
```

**Request Body:**
```json
{
  "email": "string"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully"
}
```

**Status Codes:**
- 200: OTP sent
- 400: Missing email
- 500: Email sending failed

### Verify OTP
```
POST /verify-otp
```

**Request Body:**
```json
{
  "email": "string",
  "otp": "string"
}
```

**Response:**
```json
{
  "message": "OTP verified successfully",
  "access_token": "string",
  "user": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "age": "string",
    "_id": "string"
  }
}
```

**Status Codes:**
- 200: OTP verified
- 400: Missing data or invalid OTP
- 500: Server error

### User Details
```
GET /user-details
```

**Response:**
```json
{
  "user": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "age": "string",
    "_id": "string"
  }
}
```

**Status Codes:**
- 200: User details retrieved
- 401: Unauthorized
- 404: User not found
- 500: Server error

## Detection Endpoints

### Fracture Prediction
```
POST /predict
```

**Request:**
- Content-Type: multipart/form-data
- Form field: file (image file)

**Response:**
```json
{
  "fracture_detected": boolean,
  "confidence": number,
  "probability": number,
  "body_region": "string",
  "model_version": "string",
  "model_accuracy": "string",
  "user_data": {
    "name": "string",
    "email": "string",
    "phone": "string",
    "age": "string",
    "_id": "string"
  }
}
```

**Status Codes:**
- 200: Prediction successful
- 400: Missing file or invalid file
- 401: Unauthorized
- 500: Processing error

#### Image Preprocessing & Augmentation Notes

The /predict endpoint internally applies a fixed preprocessing pipeline (implemented in backend/model.py) before running the ensemble of models:

- Decodes the uploaded image with PIL and converts it to RGB if needed.
- Resizes the image to 224×224 pixels.
- Converts the image to a PyTorch tensor and normalizes channels using ImageNet mean and standard deviation.
- Adds a batch dimension so the final tensor has shape (1, 3, 224, 224).

No random image augmentations (e.g., flips, random crops, rotation jitter) are applied during API inference. Those augmentations are used only during **model training** to improve robustness and generalization; the production API uses a deterministic preprocessing pipeline so the same X‑ray always yields the same prediction.

### Medical Chat
```
POST /chat
```

**Request Body:**
```json
{
  "message": "string",
  "context": {
    // Previous prediction results
  }
}
```

**Response:**
```json
{
  "response": "string"
}
```

**Status Codes:**
- 200: Response generated
- 400: Missing message
- 401: Unauthorized
- 500: Processing error

### Find Hospitals
```
POST /find_hospitals
```

**Request Body:**
```json
{
  "location": "string"
}
```

**Response:**
```json
{
  "link": "string" // Google Maps URL
}
```

**Status Codes:**
- 200: Link generated
- 400: Missing location
- 401: Unauthorized
- 500: Processing error

## Report Endpoints

### Get User Reports
```
GET /user-reports
```

**Response:**
```json
{
  "reports": [
    {
      "_id": "string",
      "user_email": "string",
      "report_data": {
        // Same structure as /predict response
      },
      "image_id": "string",
      "created_at": "date"
    }
  ]
}
```

**Status Codes:**
- 200: Reports retrieved
- 401: Unauthorized
- 500: Server error

### Get Specific Report
```
GET /report/{report_id}
```

**Response:**
```json
{
  "report": {
    "_id": "string",
    "user_email": "string",
    "report_data": {
      // Same structure as /predict response
    },
    "image_id": "string",
    "created_at": "date"
  }
}
```

**Status Codes:**
- 200: Report retrieved
- 401: Unauthorized
- 404: Report not found
- 500: Server error

### Get Report Image
```
GET /report-image/{image_id}
```

**Response:**
- Content-Type: image/jpeg
- Binary image data

**Status Codes:**
- 200: Image retrieved
- 401: Unauthorized
- 404: Image not found
- 500: Server error

## System Endpoints

### Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": number,
  "best_model": "string"
}
```

**Status Codes:**
- 200: System healthy

### Model Status
```
GET /model_status
```

**Response:**
```json
{
  "models": {
    "model_name": {
      "loaded": boolean,
      "type": "string"
    }
  },
  "best_model": "string",
  "total_loaded": number
}
```

**Status Codes:**
- 200: Status retrieved

## Error Responses

All error responses follow this format:

```json
{
  "error": "string"
}
```

Common error codes:
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Missing or invalid authentication
- 404: Not Found - Resource not found
- 500: Internal Server Error - Unexpected server error

## Rate Limiting

The API implements rate limiting to prevent abuse:
- 100 requests per hour per IP address
- 10 requests per minute for prediction endpoints

## CORS Policy

The API accepts requests from:
- http://localhost:3000
- http://127.0.0.1:3000

## Versioning

Current API version: v1

Future versions will be accessible at:
```
http://localhost:5000/v2/
```