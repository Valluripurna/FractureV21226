# FractureDetect AI – Complete System Overview

This document is the single, consolidated reference for the entire project: architecture, setup, authentication, image upload and processing, models and activations, data storage, analytics, and recommended cleanup.

---

## 1. High-Level Overview

FractureDetect AI is a full‑stack system for detecting bone fractures in X‑ray images.

- **Backend**: Flask REST API that handles authentication (JWT + OTP), image upload, fracture prediction using multiple PyTorch models, report persistence, analytics, chat guidance, and hospital lookup.
- **Models**: Several fracture‑focused CNNs (EfficientNet, ResNet50, DenseNet121, FracNet, MURA‑style DenseNet169) plus a few low‑weight generic ImageNet models. All endpoints and logic live in backend/model definitions and backend/app routes.
- **Storage**: MongoDB (Atlas or local) via PyMongo, with GridFS to store original X‑ray images. A robust in‑memory fallback exists for environments without Mongo.
- **Frontend**: React single‑page app (login/signup, upload/results, history, chat, hospital finder, PDF report generation) running at port 3000.
- **Docs**: This file plus API, model, frontend, and MongoDB notes in docs/.

---

## 2. Repository Structure (Essential Parts)

Key directories and files:

- Backend runtime code
  - [backend/app.py](backend/app.py) – main Flask app and all REST endpoints.
  - [backend/model.py](backend/model.py) – model architectures, loading, preprocessing, prediction, annotated image generation.
  - [backend/database.py](backend/database.py) – MongoDB + GridFS, in‑memory fallback, analytics aggregation.
  - [backend/auth.py](backend/auth.py) – OTP generation/verification and email sending.
  - [backend/background_evaluator.py](backend/background_evaluator.py) – mock evaluation to choose a “best” model.
  - [backend/generate_mock_metrics.py](backend/generate_mock_metrics.py) – generates PNG metrics/plots into results/.
  - [backend/requirements.txt](backend/requirements.txt) – Python dependencies.

- Frontend runtime code
  - [frontend/package.json](frontend/package.json) – React app dependencies and scripts.
  - [frontend/src/App.js](frontend/src/App.js) – main React component, orchestrates views and business logic.
  - [frontend/src/App.css](frontend/src/App.css) – global styling.
  - [frontend/src/components/Login.js](frontend/src/components/Login.js) – login + OTP UI.
  - [frontend/src/components/Signup.js](frontend/src/components/Signup.js) – signup UI.
  - [frontend/src/components/History.js](frontend/src/components/History.js) – report history view.
  - [frontend/src/components/Auth.css](frontend/src/components/Auth.css) – auth-specific styling.
  - [frontend/src/components/History.css](frontend/src/components/History.css) – history styling.

- Models & metrics
  - [models](models) – *.pth weights for fracture models.
  - [results](results) – PNG metrics for training curves, confusion matrices, ROC curves, etc., served by the backend for the frontend “Outputs” panel and PDF.

- Documentation (reference only, not required to run)
  - [docs/END_TO_END_GUIDE.md](docs/END_TO_END_GUIDE.md)
  - [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
  - [docs/MODEL_DOCUMENTATION.md](docs/MODEL_DOCUMENTATION.md)
  - [docs/FRONTEND_COMPONENTS.md](docs/FRONTEND_COMPONENTS.md)
  - [docs/MONGODB_INTEGRATION.md](docs/MONGODB_INTEGRATION.md)
  - [docs/README.md](docs/README.md)

- Tests and utilities (for development)
  - [tests](tests) and multiple test_*.py files at the repo root.
  - [scripts](scripts) – model creation, analysis, and loading tests.

---

## 3. Backend Setup and Run Instructions

### 3.1 Prerequisites

- Python 3.9+.
- MongoDB instance (local or Atlas). If Mongo is unavailable, the system falls back to an in‑memory store for users/reports.
- SMTP account for OTP emails (Gmail or other provider).

### 3.2 Installing Dependencies

From the repository root:

```bash
cd backend
pip install -r requirements.txt
```

If PyTorch or torchvision fail to install from requirements, install them directly from the official PyTorch instructions for your OS and hardware.

### 3.3 Environment Configuration

Set these environment variables (for example via a .env file or your shell):

- Email / OTP configuration (used in backend/auth.py):
  - EMAIL_USER – email address used to send OTP.
  - EMAIL_PASS – SMTP password or app password.
  - SMTP_SERVER – e.g. smtp.gmail.com.
- MongoDB connection (used in backend/database.py and backend/app.py):
  - MONGO_URI – e.g. mongodb://localhost:27017/fracture_detection or your Atlas URI.
- Optional verbosity flag:
  - APP_VERBOSE=1 to enable detailed logs from app.py.

### 3.4 Model Weights

Place the following files in the models directory:

- models/efficientnet_fracture_model.pth
- models/resnet50_fracture_model.pth
- models/densenet121_fracture_model.pth
- models/fracnet_model.pth
- models/mura_model_pytorch.pth

These are referenced by MODEL_PATHS in backend/app.py.

### 3.5 Starting the Backend

From backend:

```bash
python app.py
```

This starts Flask on http://0.0.0.0:5000.

### 3.6 Health and Status Endpoints

- GET /health
  - Returns overall status, number of models loaded, and current best_model.
- GET /model_status
  - Returns each loaded model’s type plus total_loaded and best_model.

---

## 4. Frontend Setup and Run Instructions

The frontend is a React application in frontend/.

### 4.1 Install Dependencies

From the repository root:

```bash
cd frontend
npm install
```

### 4.2 Run the Dev Server

```bash
npm start
```

The app runs at http://localhost:3000.

### 4.3 Backend/Frontend Integration

- CORS in backend/app.py allows:
  - http://localhost:3000
  - http://127.0.0.1:3000
- Frontend uses axios in frontend/src/App.js to call the backend at http://localhost:5000.

---

## 5. Authentication: Signup, Login, and OTP

Authentication flows span backend/app.py, backend/auth.py, backend/database.py, and frontend components.

### 5.1 Signup (Email + Password)

**Frontend**

- User opens the signup view (hash route #signup).
- frontend/src/components/Signup.js submits a POST /signup request with JSON:
  - { name, email, password, phone?, age? }.

**Backend**

- backend/app.py /signup endpoint:
  - Validates name, email, password.
  - Calls register_user in backend/database.py.
- backend/database.py register_user:
  - Hashes password with SHA‑256.
  - Stores { name, email, hashed_password, phone, age, created_at } in the users collection.
  - If Mongo fails, enables an in‑memory store and retries.

### 5.2 Login (Email + Password)

**Frontend**

- frontend/src/components/Login.js posts to /login with { email, password }.
- On success, it stores the access_token (JWT) in localStorage and passes user object to App.js via onLoginSuccess.

**Backend**

- backend/app.py /login endpoint:
  - Validates inputs.
  - Calls authenticate_user in backend/database.py, which compares the stored SHA‑256 hash.
  - If valid, creates a JWT via create_access_token(identity=email).
  - Returns JSON: { message, access_token, user }.

Protected endpoints later use the JWT via @jwt_required() and get_jwt_identity().

### 5.3 OTP-based Login

**Send OTP**

- Frontend calls POST /send-otp with { email }.
- backend/auth.py send_otp:
  - Generates a 6-digit OTP.
  - Stores it in a process memory dict with a 10‑minute expiry.
  - Attempts to email the OTP using EMAIL_USER/EMAIL_PASS/SMTP_SERVER.
  - If email configuration is missing, returns a success flag and includes the OTP in the response for development.

**Verify OTP**

- Frontend calls POST /verify-otp with { email, otp }.
- backend/app.py /verify-otp route:
  - Validates the OTP using verify_otp from backend/auth.py.
  - If the user does not yet exist, creates a minimal account with a generated placeholder password and default name.
  - Issues a JWT access token and returns { message, access_token, user }.

**User Details**

- GET /user-details (JWT required) returns the sanitized user document without password.

---

## 6. Frontend User Flow

The main user experience is implemented in frontend/src/App.js and related components.

1. **Authentication**
   - On load, App reads the location hash to determine if it should show login, signup, history, or main app view.
   - Login or signup sends credentials/OTP to the backend and stores the returned JWT and user in state.

2. **Image Upload**
   - Users can select a file via file input or drag-and-drop.
   - App.js uses FileReader to create a DataURL preview and stores the original File in state.

3. **Prediction Request**
   - App constructs a FormData with a file field and POSTs to /predict.
   - If a JWT token is present, it includes Authorization: Bearer <token>.

4. **Display Results**
   - The response includes fracture_detected, confidence, probability, body_region, model_version, model_accuracy, and optionally annotated_image.
   - App shows a detailed result card and enables actions:
     - Voice playback (including Telugu support) via the Web Speech API.
     - Download a multi-page PDF report via jsPDF.
     - Show metrics in an Outputs panel using images from /metrics/.
     - Open the chat assistant and hospital finder.

5. **History**
   - When the user opens the History view, frontend/src/components/History.js fetches /user-reports and displays a list of past scans.
   - Clicking or hovering can load associated images from /report-image/<image_id>.

---

## 7. Backend Prediction Pipeline

The prediction pipeline is split between backend/app.py and backend/model.py.

### 7.1 Image Preprocessing (Inference)

The backend applies a consistent preprocessing pipeline to every uploaded X‑ray before it reaches the models. This is implemented in preprocess_image in backend/model.py:

1. **Decode and normalize format**
  - Load the uploaded file bytes into a PIL Image.
  - Convert to RGB if the image is grayscale or has fewer channels.
2. **Geometric & numeric normalization**
  - Resize the image to 224×224 pixels (the canonical input size for the CNN backbones).
  - Convert the image to a PyTorch tensor with pixel values in [0,1].
3. **Channel-wise standardization**
  - Normalize each channel using ImageNet statistics:
    - mean = [0.485, 0.456, 0.406]
    - std  = [0.229, 0.224, 0.225]
  - This aligns the input distribution with the pretraining regime of ResNet, DenseNet, and EfficientNet.
4. **Batch dimension**
  - Add a batch dimension to produce a tensor of shape (1, 3, 224, 224).

Note: At inference time, **no random augmentations** (flips, random crops, etc.) are applied. The pipeline is intentionally deterministic so that the same X‑ray always produces the same prediction.

### 7.2 Image Augmentation (Training)

While the production API uses only deterministic preprocessing, the models behind it were trained with several forms of data augmentation to improve robustness. As summarized in docs/MODEL_DOCUMENTATION.md and the training scripts, typical augmentations include:

- **Random rotations** – simulate slight changes in patient positioning or X‑ray orientation.
- **Scaling and cropping** – help the model learn to focus on relevant bone structures regardless of zoom level.
- **Brightness and contrast jitter** – make the model less sensitive to exposure differences between machines and hospitals.
- **Occasional flips or perspective changes** (where clinically appropriate) – encourage invariance to minor pose changes.

These augmentations are applied only during training to increase the effective size and diversity of the dataset. They are *not* applied during prediction, where we want a stable, repeatable pipeline.

### 7.3 Model Architectures and Activations

Models are defined in backend/model.py.

- MURAModel (DenseNet‑169 backbone)
  - Uses models.densenet169(pretrained=True) as feature extractor.
  - Classifier:
    - AdaptiveAvgPool2d((1,1)) → Flatten → Linear(1664→1) → Sigmoid.
  - Activation: ReLU appears in the DenseNet blocks; final classifier uses Sigmoid for probability.

- EfficientNetFractureModel
  - Base: models.efficientnet_b4.
  - Customized classifier:
    - Dropout → Linear(num_features→256) → BatchNorm1d → ReLU (hidden activation) → Dropout → Linear(256→1) → Sigmoid.

- FracNetModel (ResNet50-style backbone)
  - Backbone: models.resnet50 with the fc layer replaced by Identity.
  - Fracture head:
    - AdaptiveAvgPool2d → Flatten → Linear(2048→256) → BatchNorm1d → ReLU → Dropout → Linear(256→1) → Sigmoid.

- ResNet50FractureModel
  - resnet50.fc = Sequential(Linear(2048→1), Sigmoid).

- DenseNetFractureModel
  - densenet121.classifier = Sequential(Linear(1024→1), Sigmoid).

- Generic ImageNet models (experimental)
  - GenericResNet101Model, GenericMobileNetV3Model, GenericResNeXt50Model:
    - Replace the original classification head with Linear(...→1) + Sigmoid.
  - These are not fracture-specific and are given very low weight in the ensemble.

**Key activation behavior**

- All fracture models output a single probability in [0,1] using Sigmoid.
- Hidden fully‑connected layers use ReLU as activation.
- The prediction helper does not apply Sigmoid again to avoid skewing outputs toward 0.5.

### 7.4 Single Model Prediction

predict_fracture in backend/model.py:

1. Runs the model in torch.no_grad().
2. Handles different tensor shapes and extracts a scalar probability.
3. Clamps the output to [0,1].
4. Returns the final probability.

### 7.5 Ensemble and Final Decision

In the /predict endpoint in backend/app.py:

1. For each model in loaded_models:
   - Compute prob_i = predict_fracture(model_i, input_tensor).
   - Assign a weight w_i based on model trust level; for example:
     - resnet50_fracture_model: 1.00
     - densenet121_fracture_model: 0.98
     - mura_model_pytorch: 0.85
     - efficientnet_fracture_model: 0.70
     - fracnet_model: 0.65
     - generic_*: very low weights (0.06–0.08).

2. Compute the weighted average probability:

   p_final = (Σ_i prob_i × w_i) / (Σ_i w_i).

3. Determine fracture presence:
   - fracture_detected = (p_final > 0.5).

4. Compute confidence:
   - If fracture: confidence = p_final.
   - If no fracture: confidence = 1 − p_final.

5. Choose model_version as the name of the highest‑weight model participating.

6. Create report_data with fields:
   - fracture_detected, probability, confidence, body_region, model_version, model_accuracy, user_data.

7. Generate an annotated image via create_annotated_image; attach it if available.

8. If a JWT user is present, save the report and original image into MongoDB/GridFS via save_report.

### 7.6 Annotated Image Generation

create_annotated_image in backend/model.py:

- Resizes the image to a standard 800×800.
- Draws bounding boxes that highlight likely fracture regions.
- Chooses red/yellow color and label text depending on confidence and fracture_detected.
- Renders labels using a small font, then returns a base64‑encoded PNG string.

---

## 8. Model Loading and Best Model Selection

### 8.1 Initialization at Startup

When app.py is imported, initialize_models is called inside an app context:

1. Pings MongoDB with db.command('ping') to verify connectivity.
2. Iterates over MODEL_PATHS and loads each existing .pth file via load_model.
3. Adds optional generic ImageNet models (ResNet101, MobileNetV3, ResNeXt50) with low ensemble weights.
4. Calls evaluate_models from backend/background_evaluator.py to pick best_model_name.
5. Ensures metrics PNGs exist in results/ by calling generate_mock_metrics if needed.

### 8.2 Mock Evaluation Logic

backend/background_evaluator.py uses a simple lookup table:

- resnet50_model: 0.94
- densenet_model: 0.93
- efficientnet_model: 0.95
- fracnet_model: 0.91
- mura_model: 0.89
- rsna_model: 0.87
- vindr_model: 0.88
- txv_all: 0.90

The highest score determines best_model_name. This is mainly used for status reporting and UI; the /predict endpoint still uses a full ensemble.

---

## 9. Data Storage, History, and Analytics

All persistence logic is implemented in backend/database.py.

### 9.1 MongoDB and In‑Memory Fallback

- Primary storage uses MongoDB:
  - Database: fracture_detection (by default).
  - Collections: users, reports.
  - GridFS bucket: images via gridfs.GridFS.
- If MongoDB errors occur at runtime, the code switches to an in-memory store:
  - User data kept in a dict keyed by email.
  - Reports and images stored in memory.

### 9.2 Users

- register_user: creates a new user (either in MongoDB or memory), storing a SHA‑256 hashed password.
- authenticate_user: validates email and password.
- get_user_details: returns user info without the password.

### 9.3 Reports and Images

- save_report(user_email, report_data, image_data):
  - Stores report_data and created_at.
  - If image_data exists, stores it in GridFS (or memory) and records image_id.
- get_user_reports(user_email):
  - Returns all reports for a given user, sorted by created_at, with stringified IDs.
- get_report_by_id(report_id):
  - Retrieves a single report by ID.
- get_image_by_id(image_id):
  - Returns a file-like object for the image, from GridFS or memory.

These are exposed by routes /user-reports, /report/<report_id>, and /report-image/<image_id> in backend/app.py.

### 9.4 Analytics

Function get_analytics_summary in backend/database.py computes:

- total_scans – number of reports in a given time window (default 30 days).
- scans_per_day – date/count pairs.
- fracture_rate – fraction of scans with fracture_detected == true.
- average_confidence – average of report_data.confidence.
- body_region_distribution – counts per body_region.

Route /admin/analytics (JWT required) returns this summary for use in dashboards.

---

## 10. Medical Chat and Hospital Search

### 10.1 Medical Chat (/chat)

- Endpoint: POST /chat.
- Request body:
  - message: user’s question.
  - context: optional prediction context, e.g. { fracture_detected, confidence, body_region }.
- Logic:
  - Looks for keywords like diet, medicine, pain, exercise, timeline.
  - Generates structured advice with bullet-style lines.
  - Uses context to adjust tone (e.g., fracture detected vs not detected).

This is used by the frontend chat widget to provide simple, rule‑based guidance alongside the prediction.

### 10.2 Hospital Finder

- /find_hospitals (JWT required):
  - Accepts a text location and returns a Google Maps search link for hospitals near that location.
- /nearby_hospitals (no auth):
  - Accepts JSON { latitude, longitude }.
  - Queries OpenStreetMap Overpass API for hospital nodes around the coordinates.
  - Uses a Haversine function to compute distances in kilometers.
  - Normalizes address, specialties (e.g. Orthopedics, Emergency), and returns up to five nearest hospitals.
  - If Overpass fails, falls back to a static list of sample hospitals.

The frontend uses these endpoints to fill hospital cards on the PDF and the UI.

---

## 11. Training, Augmentation, and Model Quality

Detailed training information is in docs/MODEL_DOCUMENTATION.md; this section summarizes the essentials.

### 11.1 Training Data

- MURA dataset (musculoskeletal radiographs of hand, wrist, elbow, etc.).
- RSNA and VinDr datasets.
- Additional custom fracture datasets.

### 11.2 Training Pipeline

- Transfer learning from ImageNet:
  - Start from pretrained CNNs like ResNet50, DenseNet121, EfficientNet.
  - Replace/extend the final classification layers.
- Data augmentation:
  - Random rotations.
  - Scaling and cropping.
  - Brightness and contrast changes.
  - These augmentations are used during training (not at inference) to improve generalization.
- Optimization:
  - Loss: Binary Cross‑Entropy (suitable for Sigmoid outputs).
  - Optimizer: Adam.
  - Typical hyperparameters:
    - Learning rate ~0.001, with scheduling.
    - Batch size ~32.
    - 50–100 epochs.

### 11.3 How the Model Identifies Fractures

- Convolutional layers learn low‑level features (edges, textures) and higher‑level structures (bone shapes, joint alignments).
- The final dense layers learn to map these features to a fracture probability, emphasizing cues like cortical discontinuity, abnormal angulation, and localized density changes.
- The ensemble aggregates strengths of different architectures, reducing the risk of overfitting to any specific representation.

---

## 12. Testing and Validation

Tests are not required to run the system but are useful in development.

- Root‑level tests:
  - test_predict.py, test_predict_no_auth.py – exercise prediction endpoints.
  - test_endpoints.py, test_communication.py – general API communication tests.
  - test_gridfs.py, test_local_mongodb.py – storage integration tests.

- Model tests in tests/:
  - test_models.py, test_efficientnet_fracture_model.py, test_fracnet_model.py, test_mura_pytorch.py.

These use the same model loading logic as the app to ensure compatibility.

---

## 13. Recommended Cleanup (What Is and Is Not Essential)

This section explains which files/directories are core to the running app and which are optional or primarily for development and research.

### 13.1 Core – Should Be Kept

- All files under:
  - backend/ that are directly imported by app.py (app, model, database, auth, background_evaluator, generate_mock_metrics, requirements.txt).
  - frontend/ (package.json, src, public, configuration) – required to run the web UI.
  - models/ – .pth weights.
  - results/ – PNG metrics used by /metrics/<filename> and by the PDF generator.
  - docs/ – documentation, including this COMPLETE_SYSTEM_OVERVIEW.md.

### 13.2 Useful for Development – Optional in a Production Export

These are useful while developing, testing, or retraining, but can be excluded from a minimal production bundle of the app:

- Tests:
  - tests/ directory.
  - Root‑level test_*.py files (e.g., test_predict.py, test_gridfs.py, etc.).
- Training and experimentation scripts:
  - Many scripts in scripts/ (e.g., analyze_models.py, create_empty_models.py, recreate_*_model.py, save_*_model.py, test_model_loading.py, etc.).
  - Training helpers in backend/ (train_fast.py, train_knowledge_distillation.py, train_simple_distillation.py, verify_models.py).
- Research and paper assets:
  - paper/ directory (LaTeX, figures, Word export tooling).
- Project tracking / one‑time docs:
  - Top‑level files like TRAINING_COMPLETION.md, PROJECT_COMPLETION.md, COMPLETE_CHANGELOG.md, train_output.txt and similar may not be needed in a clean deployment.

If your goal is a lean “runtime only” package, you can move or delete these from your deployment artifact, while keeping them in the development repository (via .gitignore or a separate branch/tag).

### 13.3 Generated Artifacts You Can Safely Delete

These are generated during development and are safe to remove at any time (they will be recreated as needed):

- Python bytecode caches:
  - backend/__pycache__/
  - scripts/__pycache__/
- Node build artifacts:
  - frontend/node_modules/ (recreated by npm install when needed).
  - frontend/build/ (if present; recreated by npm run build).

Due to restrictions of the automated editing tools here, compiled/binary files and entire directories may need to be deleted manually in your editor or file explorer, but it is safe to do so.

---

## 14. Summary

- Backend: Flask API in backend/app.py orchestrates authentication, prediction, storage, chat, and hospital search.
- Frontend: React SPA in frontend connects to the backend for signup/login, upload, results, history, and PDF generation.
- Models: Multiple fracture detectors and helper models loaded from models/, with Sigmoid final activations and ReLU inside classifier heads.
- Data: Stored in MongoDB/Atlas with GridFS; in‑memory fallback ensures graceful degradation.
- Ensemble: Weighted combination of fracture models to improve robustness and accuracy.
- Cleanup: You can keep backend/, frontend/, models/, results/, docs/ as core and treat tests/, scripts/, paper/, and various logs/completion docs as optional for production.

This file is intended to be your single source of truth when understanding, running, or packaging the FractureDetect AI project.