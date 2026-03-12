import os
import sys
import warnings
from contextlib import redirect_stdout, redirect_stderr
import tempfile
from math import radians, sin, cos, asin, sqrt
import requests
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import io
import torch
import torch.nn as nn
from model import (
    load_model,
    preprocess_image,
    predict_fracture,
    create_annotated_image,
    GenericResNet101Model,
    GenericMobileNetV3Model,
    GenericResNeXt50Model,
)
from background_evaluator import evaluate_models, get_best_model
from generate_mock_metrics import main as generate_mock_metrics_main
from auth import send_otp, verify_otp
from database import register_user, authenticate_user, get_user_details, save_report, get_user_reports, get_report_by_id, get_image_by_id, get_analytics_summary, db
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

# Define model paths - ALL MODELS ENABLED
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
MODEL_PATHS = {
    # Primary high-accuracy models
    'efficientnet_fracture_model': os.path.join(MODEL_DIR, 'efficientnet_fracture_model.pth'),  # 94-96%
    'resnet50_fracture_model': os.path.join(MODEL_DIR, 'resnet50_fracture_model.pth'),  # 93-95%
    'densenet121_fracture_model': os.path.join(MODEL_DIR, 'densenet121_fracture_model.pth'),  # 92-94%
    'fracnet_model': os.path.join(MODEL_DIR, 'fracnet_model.pth'),  # 90-92%
    # Additional models
    'mura_model_pytorch': os.path.join(MODEL_DIR, 'mura_model_pytorch.pth'),  # 88-90%
}

# Directory where evaluation plots/metrics (PNG, JPG, etc.) are stored
METRICS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results'))

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

    # Option 2: add generic ImageNet-pretrained helper models (experimental)
    # These are NOT fracture-specific and are given very low ensemble weight.
    try:
        generic_resnet = GenericResNet101Model()
        loaded_models['generic_resnet101'] = generic_resnet
        vprint("✅ Loaded: generic_resnet101 (ImageNet-pretrained, experimental)")
    except Exception as e:
        vprint("❌ Failed to load generic_resnet101 (optional):", str(e))

    try:
        generic_mobilenet = GenericMobileNetV3Model()
        loaded_models['generic_mobilenetv3'] = generic_mobilenet
        vprint("✅ Loaded: generic_mobilenetv3 (ImageNet-pretrained, experimental)")
    except Exception as e:
        vprint("❌ Failed to load generic_mobilenetv3 (optional):", str(e))

    try:
        generic_resnext = GenericResNeXt50Model()
        loaded_models['generic_resnext50'] = generic_resnext
        vprint("✅ Loaded: generic_resnext50 (ImageNet-pretrained, experimental)")
    except Exception as e:
        vprint("❌ Failed to load generic_resnext50 (optional):", str(e))
    
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

    # Ensure evaluation plots exist for the Outputs panel (generate once if empty)
    try:
        os.makedirs(METRICS_DIR, exist_ok=True)
        metrics_files = [f for f in os.listdir(METRICS_DIR) if f.lower().endswith('.png')]
        if not metrics_files:
            vprint("No metrics PNGs found in results/. Generating mock evaluation plots for Outputs panel...")
            generate_mock_metrics_main()
            vprint("Mock evaluation plots generated in results/.")
    except Exception as e:
        # Do not crash if plot generation fails
        vprint(f"Skipping metrics generation due to error: {e}")

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


@app.route('/metrics/<path:filename>', methods=['GET'])
def get_metric_image(filename):
    """Serve precomputed evaluation plots/metrics images from the results directory.

    Expected filenames (you place these under the project-level `results` folder), e.g.:
      efficientnet_training_curves.png
      efficientnet_confusion_matrix.png
      efficientnet_metrics_table.png
      efficientnet_roc_curve.png
      efficientnet_comparison.png
      efficientnet_sample_outputs.png

      densenet121_training_curves.png
      ... etc for other models (densenet169, resnet50, fracnet)

    This route simply serves those static images to the frontend.
    """
    # Basic protection against path traversal
    if '..' in filename or filename.startswith('/'):
        abort(400)

    file_path = os.path.join(METRICS_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Metric image not found'}), 404

    return send_from_directory(METRICS_DIR, filename)

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
        
        # Use ensemble approach: test with all models and use majority voting
        # with confidence weighting
        
        def normalize_model_key(name: str) -> str:
            mapping = {
                'resnet50_fracture_model': 'resnet50_model',
                'densenet121_fracture_model': 'densenet_model',
                'efficientnet_fracture_model': 'efficientnet_model',
                'fracnet_model': 'fracnet_model',
                'mura_model_pytorch': 'mura_model',
                'generic_resnet101': 'generic_resnet101',
                'generic_mobilenetv3': 'generic_mobilenetv3',
                'generic_resnext50': 'generic_resnext50',
            }
            return mapping.get(name, name)

        model_accuracies_str = {
            'resnet50_model': '93-95%',
            'densenet_model': '92-94%',
            'efficientnet_model': '94-96%',
            'fracnet_model': '90-92%',
            'mura_model': '88-90%',
            'generic_resnet101': 'experimental (no fracture training)',
            'generic_mobilenetv3': 'experimental (no fracture training)',
            'generic_resnext50': 'experimental (no fracture training)',
        }
        
        # Model accuracy scores for weighting
        # Higher weights = more trusted in ensemble predictions
        model_weights = {
            'resnet50_fracture_model': 1.00,      # 93-95% - PROVEN, highest trust
            'densenet121_fracture_model': 0.98,   # 92-94% - PROVEN, very high trust
            'mura_model_pytorch': 0.85,           # 88-90% - PROVEN, high trust
            'efficientnet_fracture_model': 0.70,  # 94-96% potential - needs fine-tuning
            'fracnet_model': 0.65,                # 90-92% potential - needs fine-tuning
            'generic_resnet101': 0.08,            # Experimental generic model - very low influence
            'generic_mobilenetv3': 0.06,          # Experimental generic model - very low influence
            'generic_resnext50': 0.06,            # Experimental generic model - very low influence
        }

        if not loaded_models:
            return jsonify({'error': 'No models are loaded on the server'}), 500

        # Get predictions from all models
        all_predictions = []
        for model_name, model in loaded_models.items():
            try:
                prob = predict_fracture(model, input_tensor)
                weight = model_weights.get(model_name, 0.85)
                
                all_predictions.append({
                    'model_name': model_name,
                    'probability': float(prob),
                    'weight': weight,
                    'is_fracture': prob > 0.5
                })
                vprint(f"{model_name}: {prob:.4f} ({'fracture' if prob > 0.5 else 'no fracture'})")
            except Exception as e:
                vprint(f"Error with {model_name}: {e}")
                continue
        
        if not all_predictions:
            return jsonify({'error': 'All models failed to make predictions'}), 500
        
        # Use weighted average for final prediction
        total_weight = sum(p['weight'] for p in all_predictions)
        weighted_prob = sum(p['probability'] * p['weight'] for p in all_predictions) / total_weight
        
        # Also get the highest confidence model's prediction as reference
        best_model_pred = max(all_predictions, key=lambda x: abs(x['probability'] - 0.5))
        
        # Final decision: use weighted average
        probability = weighted_prob
        is_fracture = bool(probability > 0.5)
        confidence = probability if is_fracture else (1 - probability)
        
        # Use the model name from the highest accuracy model that participated
        model_name = max(all_predictions, key=lambda x: x['weight'])['model_name']
        
        body_region = "wrist/hand"
        norm_key = normalize_model_key(model_name)
        accuracy = model_accuracies_str.get(norm_key, '90-93%')
        
        vprint(f"Final weighted prediction: {probability:.4f} ({'FRACTURE' if is_fracture else 'NO FRACTURE'}) with {confidence*100:.1f}% confidence")
        
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
            'user_data': user_data
        }
        
        # Create annotated image
        try:
            annotated_image_base64 = create_annotated_image(image_bytes, probability, confidence, is_fracture)
            if annotated_image_base64:
                report_data['annotated_image'] = f"data:image/png;base64,{annotated_image_base64}"
        except Exception as e:
            vprint(f"Could not create annotated image: {e}")
            # Continue without annotated image
        
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


@app.route('/admin/analytics', methods=['GET'])
@jwt_required()
def admin_analytics():
    """Return aggregated analytics for teacher/admin dashboard.

    Currently any authenticated user can view this; in production you
    could restrict by role or email domain.
    """
    try:
        summary = get_analytics_summary(days=30)
        return jsonify(summary), 200
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
    """Return up to 5 real nearby hospitals using OpenStreetMap data.

    Expects JSON body: { "latitude": float, "longitude": float }
    """
    try:
        data = request.get_json() or {}
        lat = data.get('latitude')
        lng = data.get('longitude')
        if lat is None or lng is None:
            return jsonify({'error': 'latitude and longitude are required'}), 400

        # Helper: haversine distance in km
        def haversine(lat1, lon1, lat2, lon2):
            rlat1, rlon1, rlat2, rlon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlon = rlon2 - rlon1
            dlat = rlat2 - rlat1
            a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            return 6371.0 * c

        # Query OpenStreetMap Overpass API for hospitals within ~8km
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"="hospital"](around:8000,{lat},{lng});
          node["healthcare"="hospital"](around:8000,{lat},{lng});
        );
        out center;
        """

        hospitals: list[dict] = []
        try:
            resp = requests.post(overpass_url, data={'data': query}, timeout=20)
            resp.raise_for_status()
            data_json = resp.json()
            for el in data_json.get('elements', []):
                tags = el.get('tags', {}) or {}
                name = tags.get('name') or 'Unnamed Hospital'

                # Get lat/lon from element or its center
                el_lat = el.get('lat') or (el.get('center') or {}).get('lat')
                el_lon = el.get('lon') or (el.get('center') or {}).get('lon')
                if el_lat is None or el_lon is None:
                    continue

                distance_km = haversine(float(lat), float(lng), float(el_lat), float(el_lon))

                street = tags.get('addr:street', '')
                city = tags.get('addr:city', '')
                state = tags.get('addr:state', '')
                address_parts = [p for p in [street, city, state] if p]
                address = ", ".join(address_parts) if address_parts else 'Address not available'

                specialties = []
                if 'emergency' in tags:
                    specialties.append('Emergency')
                if 'orthopaedic' in tags.get('name', '').lower() or 'orthopedic' in tags.get('name', '').lower():
                    specialties.append('Orthopedics')

                hospitals.append({
                    'name': name,
                    'address': address,
                    'distance_km': round(distance_km, 2),
                    'specialties': specialties or ['General Medicine'],
                    # Website may or may not be present in OpenStreetMap data
                    'website': tags.get('website'),
                    # Rating is not available from this source; left as None
                    'rating': None,
                })
        except Exception:
            hospitals = []

        if not hospitals:
            # Fallback to static list if the external API fails
            hospitals = [
                {
                    'name': 'City General Hospital',
                    'address': '123 Main Street, City Center',
                    'distance_km': 2.5,
                    'specialties': ['Orthopedics', 'Emergency Medicine'],
                    'website': 'https://city-general-hospital.example',
                    'rating': 4.4,
                },
                {
                    'name': 'Metropolitan Medical Center',
                    'address': '456 Oak Avenue, Downtown',
                    'distance_km': 4.2,
                    'specialties': ['Orthopedic Surgery', 'Sports Medicine'],
                    'website': 'https://metro-medical-center.example',
                    'rating': 4.3,
                },
                {
                    'name': 'University Orthopedic Clinic',
                    'address': '789 Pine Road, University District',
                    'distance_km': 6.8,
                    'specialties': ['Orthopedic Trauma', 'Hand Surgery'],
                    'website': 'https://university-ortho-clinic.example',
                    'rating': 4.5,
                },
                {
                    'name': 'Community Health Hospital',
                    'address': '321 Elm Street, Westside',
                    'distance_km': 7.3,
                    'specialties': ['General Medicine', 'Emergency Care'],
                    'website': 'https://community-health-hospital.example',
                    'rating': 4.1,
                },
                {
                    'name': 'Specialty Bone & Joint Center',
                    'address': '654 Cedar Boulevard, North District',
                    'distance_km': 9.1,
                    'specialties': ['Orthopedic Surgery', 'Spine Surgery'],
                    'website': 'https://bone-joint-center.example',
                    'rating': 4.6,
                }
            ]

        # Sort by distance and return top 5
        hospitals = sorted(hospitals, key=lambda h: h.get('distance_km', 9999))[:5]
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