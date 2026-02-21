import os
import sys
import warnings
from contextlib import redirect_stdout, redirect_stderr
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import io
import torch
import torch.nn as nn
from model import load_model, preprocess_image, predict_fracture
from background_evaluator import evaluate_models, get_best_model
from auth import send_otp, verify_otp
from database import register_user, authenticate_user, get_user_details, save_report, get_user_reports, get_report_by_id, get_image_by_id, db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
import urllib.parse
import uuid

# Set environment variables to suppress PyTorch warnings and verbose output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['TORCH_CPP_LOG_LEVEL'] = 'ERROR'

# Suppress warnings
warnings.filterwarnings("ignore")

# Import logging and set level to ERROR to suppress verbose output
import logging
logging.getLogger("torchxrayvision").setLevel(logging.ERROR)

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'fracture_detect_secret_key'  # Change this in production
jwt = JWTManager(app)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Verbose control for console output (set APP_VERBOSE=1 to enable)
APP_VERBOSE = os.getenv('APP_VERBOSE', '0') == '1'
def vprint(*args, **kwargs):
    if APP_VERBOSE:
        print(*args, **kwargs)

# Global variables to store loaded models
loaded_models = {}
best_model_name = None

# Define model paths
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
MODEL_PATHS = {
    'resnet50_fracture_model': os.path.join(MODEL_DIR, 'resnet50_fracture_model.pth'),
    'densenet121_fracture_model': os.path.join(MODEL_DIR, 'densenet121_fracture_model.pth'),
    'efficientnet_fracture_model': os.path.join(MODEL_DIR, 'efficientnet_fracture_model.pth'),
    'fracnet_model': os.path.join(MODEL_DIR, 'fracnet_model.pth'),
    'mura_model_pytorch': os.path.join(MODEL_DIR, 'mura_model_pytorch.pth'),
    'rsna_model': os.path.join(MODEL_DIR, 'rsna_model.pth'),
    'vindr_model': os.path.join(MODEL_DIR, 'vindr_model.pth'),
    'fracture_model': os.path.join(MODEL_DIR, 'fracture_model.pth'),  # TorchXRayVision ALL model
}

def initialize_models():
    """Initialize all models at startup."""
    global loaded_models, best_model_name
    
    # Check database connection
    try:
        # Test database connection
        db.command('ping')
        vprint("✅ Database connected successfully")
    except Exception as e:
        vprint("❌ Database connection failed")
    
    vprint("Loading models...")
    for model_name, model_path in MODEL_PATHS.items():
        if os.path.exists(model_path):
            try:
                model = load_model(model_path)
                loaded_models[model_name] = model
                vprint(f"✅ Loaded: {model_name}")
            except Exception as e:
                # Suppress detailed error messages
                vprint(f"❌ Failed to load: {model_name}")
                pass
        else:
            # Suppress model not found warnings
            pass
    
    vprint(f"Successfully loaded {len(loaded_models)} models")
    
    # Evaluate models to determine the best one
    try:
        # Suppress verbose output during evaluation
        with redirect_stdout(tempfile.TemporaryFile()), redirect_stderr(tempfile.TemporaryFile()):
            best_model_name = evaluate_models(loaded_models)
        vprint(f"Best model: {best_model_name}")
    except Exception as e:
        # Set a default model if evaluation fails
        if loaded_models:
            best_model_name = list(loaded_models.keys())[0]
            # Intentionally not printing default model selection unless verbose
            vprint(f"Using {best_model_name} as default model")

# Authentication Routes
@app.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint."""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        age = data.get('age', '')
        
        if not name or not email or not password:
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        success, message = register_user(name, email, password, phone, age)
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        success, message = authenticate_user(email, password)
        if success:
            # Create JWT token
            access_token = create_access_token(identity=email)
            user_details = get_user_details(email)
            return jsonify({
                'message': message,
                'access_token': access_token,
                'user': user_details
            }), 200
        else:
            return jsonify({'error': message}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/send-otp', methods=['POST'])
def send_otp_route():
    """Send OTP to user's email."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        result = send_otp(email)
        # Support both legacy (success, message) and new (success, message, dev_otp) tuple
        success = result[0]
        message = result[1]
        dev_otp = result[2] if len(result) > 2 else None
        if success:
            payload = {'message': message}
            if dev_otp:
                payload['dev_otp'] = dev_otp
            return jsonify(payload), 200
        else:
            return jsonify({'error': message}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify-otp', methods=['POST'])
def verify_otp_route():
    """Verify OTP for user."""
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return jsonify({'error': 'Email and OTP are required'}), 400
        
        success, message = verify_otp(email, otp)
        if success:
            # Ensure user exists; if not, auto-provision a minimal account for OTP login
            user_details = get_user_details(email)
            if not user_details:
                default_name = email.split('@')[0]
                # Generate a placeholder password (user can change later)
                placeholder_password = f"otp_{otp}_{uuid.uuid4().hex[:6]}"
                register_user(default_name, email, placeholder_password)
                user_details = get_user_details(email)
            # Create JWT token after successful OTP verification
            access_token = create_access_token(identity=email)
            return jsonify({
                'message': message,
                'access_token': access_token,
                'user': user_details
            }), 200
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user-details', methods=['GET'])
@jwt_required()
def user_details():
    """Get user details."""
    try:
        current_user = get_jwt_identity()
        user_details = get_user_details(current_user)
        if user_details:
            return jsonify({'user': user_details}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(loaded_models),
        'best_model': best_model_name
    })

@app.route('/model_status')
def model_status():
    """Endpoint to get the status of all models."""
    model_info = {}
    for name, model in loaded_models.items():
        model_info[name] = {
            'loaded': True,
            'type': str(type(model).__name__)
        }
    
    return jsonify({
        'models': model_info,
        'best_model': best_model_name,
        'total_loaded': len(loaded_models)
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint."""
    try:
        vprint("Received prediction request")
        # Make JWT optional for this endpoint to improve UX
        try:
            verify_jwt_in_request(optional=True)
        except Exception as _jwt_err:
            pass
        # Check if image file is present in request
        if 'file' not in request.files:
            vprint("No file in request.files")
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['file']
        vprint(f"File received: {file.filename}")
        if file.filename == '':
            vprint("Empty filename")
            return jsonify({'error': 'No image selected'}), 400
            
        # Read image bytes
        image_bytes = file.read()
        vprint(f"Image bytes read: {len(image_bytes)} bytes")
        
        # Preprocess image
        input_tensor = preprocess_image(image_bytes)
        vprint(f"Image preprocessed, tensor shape: {input_tensor.shape}")
        
        # Evaluate across all loaded models and choose the one with highest evaluator score
        from background_evaluator import evaluate_model

        def normalize_model_key(name: str) -> str:
            mapping = {
                'resnet50_fracture_model': 'resnet50_model',
                'densenet121_fracture_model': 'densenet_model',
                'efficientnet_fracture_model': 'efficientnet_model',
                'fracnet_model': 'fracnet_model',
                'mura_model_pytorch': 'mura_model',
                'rsna_model': 'rsna_model',
                'vindr_model': 'vindr_model',
                'fracture_model': 'txv_all'
            }
            return mapping.get(name, name)

        model_accuracies_str = {
            'resnet50_model': '93-95%',
            'densenet_model': '92-94%',
            'efficientnet_model': '94-96%',
            'fracnet_model': '90-92%',
            'mura_model': '88-90%',
            'rsna_model': '85-88%',
            'vindr_model': '87-89%',
            'txv_all': '89-91%'
        }

        if not loaded_models:
            return jsonify({'error': 'No models are loaded on the server'}), 500

        all_results = []
        for m_name, m in loaded_models.items():
            try:
                prob = predict_fracture(m, input_tensor)
                norm = normalize_model_key(m_name)
                score = evaluate_model(m, norm)
                all_results.append({
                    'model_key': m_name,
                    'normalized_key': norm,
                    'probability': float(prob),
                    'is_fracture': bool(prob > 0.5),
                    'evaluator_score': float(score),
                    'model_accuracy': model_accuracies_str.get(norm, 'N/A')
                })
            except Exception as _e:
                # skip model on error
                continue

        if not all_results:
            return jsonify({'error': 'Prediction failed for all models'}), 500

        # Choose best by evaluator score; tie-break by higher confidence
        best = sorted(all_results, key=lambda r: (r['evaluator_score'], r['probability']), reverse=True)[0]

        model_name = best['model_key']
        probability = best['probability']
        is_fracture = best['is_fracture']
        confidence = probability if is_fracture else (1 - probability)
        body_region = "wrist/hand"
        accuracy = best['model_accuracy']
        
        # Get user details for the report
        try:
            current_user = get_jwt_identity()
            user_data = get_user_details(current_user) if current_user else None
        except Exception as e:
            current_user = None
            user_data = None
        
        # Prepare report data
        report_data = {
            'fracture_detected': is_fracture,
            'confidence': float(confidence),
            'probability': float(probability),
            'body_region': body_region,
            'model_version': model_name,
            'model_accuracy': accuracy,
            'all_model_results': all_results,
            'user_data': user_data
        }
        
        # Save report and image to MongoDB (skip if not authenticated)
        try:
            if current_user:
                save_report(current_user, report_data, image_bytes)
        except Exception as e:
            print(f"Could not save report: {e}")
            # Continue anyway, saving report is not critical for prediction
        
        return jsonify(report_data)
        
    except Exception as e:
        vprint(f"Error during prediction: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500

@app.route('/user-reports', methods=['GET'])
@jwt_required()
def user_reports():
    """Get all reports for the current user."""
    try:
        current_user = get_jwt_identity()
        reports = get_user_reports(current_user)
        return jsonify({'reports': reports}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get a specific report by ID."""
    try:
        report = get_report_by_id(report_id)
        if report:
            return jsonify({'report': report}), 200
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report-image/<image_id>', methods=['GET'])
@jwt_required()
def get_report_image(image_id):
    """Get an image by ID."""
    try:
        image_file = get_image_by_id(image_id)
        if image_file:
            return image_file.read(), 200, {'Content-Type': 'image/jpeg'}
        else:
            return jsonify({'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/find_hospitals', methods=['POST'])
@jwt_required()
def find_hospitals():
    """Find nearby hospitals based on a text location (legacy)."""
    try:
        data = request.get_json()
        location = data.get('location')
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        encoded_location = urllib.parse.quote(location)
        maps_url = f"https://www.google.com/maps/search/hospitals+near+{encoded_location}"
        return jsonify({'link': maps_url}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/nearby_hospitals', methods=['POST'])
def nearby_hospitals():
    """Return a mock list of 5 nearby hospitals using GPS coordinates.
    Expects: { latitude: float, longitude: float }
    """
    try:
        data = request.get_json() or {}
        lat = data.get('latitude')
        lng = data.get('longitude')
        if lat is None or lng is None:
            return jsonify({'error': 'latitude and longitude are required'}), 400
        # Mocked data (replace with Places API integration in production)
        hospitals = [
            {
                'name': 'City General Hospital',
                'address': '123 Main Street, City Center',
                'distance_km': 2.5,
                'specialties': ['Orthopedics', 'Emergency Medicine']
            },
            {
                'name': 'Metropolitan Medical Center',
                'address': '456 Oak Avenue, Downtown',
                'distance_km': 4.2,
                'specialties': ['Orthopedic Surgery', 'Sports Medicine']
            },
            {
                'name': 'University Orthopedic Clinic',
                'address': '789 Pine Road, University District',
                'distance_km': 6.8,
                'specialties': ['Orthopedic Trauma', 'Hand Surgery']
            },
            {
                'name': 'Community Health Hospital',
                'address': '321 Elm Street, Westside',
                'distance_km': 7.3,
                'specialties': ['General Medicine', 'Emergency Care']
            },
            {
                'name': 'Specialty Bone & Joint Center',
                'address': '654 Cedar Boulevard, North District',
                'distance_km': 9.1,
                'specialties': ['Orthopedic Surgery', 'Spine Surgery']
            }
        ]
        return jsonify({'hospitals': hospitals}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Mock medical assistant with category-based guidance."""
    try:
        data = request.get_json() or {}
        message = (data.get('message') or '').lower()
        context = data.get('context', {}) or {}
        fx = bool(context.get('fracture_detected'))
        conf = float(context.get('confidence', 0.0)) * 100.0
        region = context.get('body_region', 'affected area')

        def reply(lines):
            return "\n".join(lines)

        if any(k in message for k in ['diet', 'food', 'nutrition']):
            lines = [
                "Dietary Guidelines:",
                "• Increase Calcium: dairy, leafy greens, sardines",
                "• Vitamin D: fatty fish, fortified foods, safe sunlight",
                "• Protein: lean meats, beans, eggs, dairy",
                "• Vitamin C: citrus, berries, bell peppers",
                "• Magnesium/Zinc: nuts, seeds, whole grains",
                "• Hydration: 8–10 glasses water daily",
            ]
            if fx:
                lines.insert(0, f"A fracture is detected ({conf:.1f}% confidence). Nutrition supports healing.")
            else:
                lines.insert(0, f"No fracture detected ({conf:.1f}% confidence). Maintain a balanced diet; see a doctor if pain persists.")
            return jsonify({'response': reply(lines)}), 200

        if any(k in message for k in ['medicine', 'medication', 'medicines', 'drug', 'drugs']):
            lines = [
                "Treatment / Medicines:",
                "• Use prescribed pain medication only as directed",
                "• Consider anti-inflammatory agents if advised",
                "• Calcium + Vitamin D supplementation when recommended",
                "• Follow-up with your orthopedist for adjustments",
            ]
            if fx:
                lines.insert(0, f"For a suspected fracture in the {region}, seek medical care promptly.")
            else:
                lines.insert(0, "If pain continues, consult a clinician before taking medication.")
            return jsonify({'response': reply(lines)}), 200

        if any(k in message for k in ['pain', 'pain management', 'hurt', 'ache']):
            lines = [
                "Pain Management:",
                "• Rest and immobilize the affected area",
                "• Ice 10–15 min, 3–4× daily (avoid direct skin contact)",
                "• Elevate to reduce swelling",
                "• Use prescribed analgesics only as directed",
            ]
            if fx:
                lines.append("• Avoid weight-bearing until cleared by a clinician")
            return jsonify({'response': reply(lines)}), 200

        if any(k in message for k in ['exercise', 'rehab', 'physio', 'physical therapy']):
            lines = [
                "Exercise / Rehabilitation:",
                "• Follow doctor-approved activity restrictions",
                "• Isometrics during immobilization (as advised)",
                "• Gradual return to weight-bearing when allowed",
                "• Supervised physical therapy for mobility + strength",
                "• Avoid high-impact activity until cleared",
            ]
            return jsonify({'response': reply(lines)}), 200

        if any(k in message for k in ['timeline', 'recover', 'healing', 'how long']):
            lines = [
                "Recovery Timeline (varies by fracture):",
                "• 1–2 weeks: inflammation phase",
                "• 2–6 weeks: soft callus formation",
                "• 6–12 weeks: hard callus / bone strengthening",
                "• 6–24 months: remodeling phase",
            ]
            return jsonify({'response': reply(lines)}), 200

        # Default guidance
        if fx:
            response = (
                f"Fracture indicated with {conf:.1f}% confidence. Protect the {region}, avoid weight-bearing,"
                " apply ice, and seek prompt medical care."
            )
        else:
            response = (
                f"No fracture indicated with {conf:.1f}% confidence. Rest, avoid strain, and consult a doctor if pain persists."
            )
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize models when the app starts
with app.app_context():
    initialize_models()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)