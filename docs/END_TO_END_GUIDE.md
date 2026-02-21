# FractureDetect AI End-to-End Guide

This guide walks you through the entire system: what it does, how it is structured, and step-by-step instructions to configure, run, and validate it locally.

## 1) What the System Does
- Detects bone fractures in X-ray images using an ensemble of PyTorch models (EfficientNet, ResNet50, DenseNet121, FracNet, MURA).
- Serves a Flask REST API for authentication, prediction, reporting, chat guidance, and hospital lookup.
- Stores users, reports, and X-ray binaries in MongoDB with GridFS, retaining full history.
- Provides a React frontend for upload, live results, PDF reports, chat, and history views.

## 2) Architecture at a Glance
- Frontend: React SPA (Auth, Upload/Results, Chat, History) calling the backend.
- Backend: Flask API with JWT auth, model orchestration, PDF-ready responses, and MongoDB integration.
- Models: Pretrained .pth files loaded at startup; best model auto-selected based on evaluation.
- Storage: MongoDB Atlas or local MongoDB; GridFS for image binaries.

## 3) Prerequisites
- Python 3.9+
- Node.js 14+
- MongoDB Atlas URI or local MongoDB instance
- SMTP account for OTP email (e.g., Gmail app password)
- Model weight files in the models/ directory

## 4) Project Layout
- backend/: Flask app, auth, database layer, model loading, background evaluator
- frontend/: React app with authentication, upload/results, chat, history
- models/: .pth model files
- docs/: Additional references (API, frontend components, models, MongoDB)

## 5) Step-by-Step Setup

### A. Backend
1. Move into backend:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If torch/torchvision are missing, install them explicitly for your platform.
3. Create backend/.env with your secrets:
   ```env
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   SMTP_SERVER=smtp.gmail.com
   MONGO_URI=<your mongodb uri>
   ```
4. Add model files into ../models/:
   - resnet50_fracture_model.pth
   - densenet121_fracture_model.pth
   - efficientnet_fracture_model.pth
   - fracnet_model.pth
   - mura_model_pytorch.pth
5. Start the API:
   ```bash
   python app.py
   ```
   Health checks:
   - GET http://localhost:5000/health
   - GET http://localhost:5000/model_status

### B. Frontend
1. Move into frontend:
   ```bash
   cd frontend
   ```
2. Install packages:
   ```bash
   npm install
   ```
3. Run the dev server:
   ```bash
   npm start
   ```
   Open http://localhost:3000.

## 6) Using the App (Happy Path)
1. Sign up or log in (email/password or OTP). JWT is stored client-side for API calls.
2. Upload an X-ray (JPEG/PNG/BMP/TIFF). Preview appears client-side.
3. Submit for prediction. Backend picks the best-loaded model, returns fracture flag, confidence, body region, and model metadata.
4. View results and download the PDF report (includes patient info, recommendations, and image preview).
5. Use Medical Chat for guidance and Hospital Finder for a Google Maps link.
6. Open History to see past reports and images (fetched from MongoDB + GridFS).

## 7) API Quickstart
- Base URL: http://localhost:5000
- Auth header: Authorization: Bearer <token>
- Core endpoints:
  - POST /signup, POST /login, POST /send-otp, POST /verify-otp
  - POST /predict (multipart/form-data with file)
  - GET /user-reports, GET /report/{id}, GET /report-image/{id}
  - POST /chat, POST /find_hospitals
  - GET /health, GET /model_status

## 8) Data and Storage Notes
- Users and reports live in MongoDB; images are stored via GridFS and referenced by image_id.
- Emails and passwords are SHA-256 hashed; JWT tokens expire periodically.
- Index email and created_at for fast lookups (recommended for production).

## 9) Testing and Validation
- Sanity checks: run /health and /model_status after backend start.
- API smoke tests (with a valid token): upload a small sample X-ray and confirm response fields fracture_detected and confidence.
- Frontend: verify login, upload, PDF download, chat, and history flows in the browser.
- Optional: exercise python tests with pytest from the repo root if configured for your environment.

## 10) Deployment Pointers
- Serve Flask behind a production WSGI server (e.g., gunicorn/uwsgi) and reverse proxy (Nginx/Apache) with HTTPS.
- Configure environment variables securely; never commit secrets.
- Use a managed MongoDB instance with backups; enable IP allowlisting.
- Preload models at startup and monitor memory; consider GPU instances for latency.

## 11) Troubleshooting Cheatsheet
- Models not loading: verify filenames in models/ and PyTorch install; check backend logs.
- MongoDB errors: confirm MONGO_URI, network access, and indexes; ensure collections exist on first write.
- OTP failures: recheck SMTP creds/app password and spam folder.
- CORS/frontend errors: ensure backend on 5000 and frontend on 3000; confirm allowed origins.

## 12) Where to Learn More
- API details: docs/API_DOCUMENTATION.md
- Frontend components: docs/FRONTEND_COMPONENTS.md
- Model specifics: docs/MODEL_DOCUMENTATION.md
- MongoDB design: docs/MONGODB_INTEGRATION.md
