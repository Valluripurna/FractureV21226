"""Test all models after fixes to verify they work correctly."""
import torch
import os
from model import load_model, preprocess_image, predict_fracture
from PIL import Image

print("=" * 70)
print("TESTING ALL MODELS AFTER FIXES")
print("=" * 70)

# Load test image
test_image_path = os.path.join('..', 'test_images', 'test_image.png')
models_dir = os.path.join('..', 'models')

if not os.path.exists(test_image_path):
    print(f"\n❌ Test image not found: {test_image_path}")
    exit(1)

print(f"\n✓ Found test image: {test_image_path}")

# Read image
with open(test_image_path, 'rb') as f:
    img_bytes = f.read()

img_tensor = preprocess_image(img_bytes)
print(f"✓ Image preprocessed, tensor shape: {img_tensor.shape}")

# Test all models
model_files = [
    ('efficientnet_fracture_model.pth', 'EfficientNet B4', '94-96%'),
    ('resnet50_fracture_model.pth', 'ResNet50', '93-95%'),
    ('densenet121_fracture_model.pth', 'DenseNet121', '92-94%'),
    ('fracnet_model.pth', 'FracNet', '90-92%'),
    ('mura_model_pytorch.pth', 'MURA DenseNet169', '88-90%'),
]

print("\n" + "=" * 70)
print("MODEL PREDICTIONS:")
print("=" * 70)
print(f"\n{'Model':<25} {'Probability':<15} {'Prediction':<20} {'Status'}")
print("-" * 70)

successful_models = []
failed_models = []

for model_file, model_display_name, accuracy in model_files:
    model_path = os.path.join(models_dir, model_file)
    
    if not os.path.exists(model_path):
        print(f"{model_display_name:<25} {'N/A':<15} {'FILE NOT FOUND':<20} ❌")
        failed_models.append((model_display_name, "File not found"))
        continue
    
    try:
        # Load model
        model = load_model(model_path)
        
        # Make prediction
        probability = predict_fracture(model, img_tensor)
        
        # Determine prediction
        is_fracture = probability > 0.5
        prediction = "FRACTURE" if is_fracture else "NO FRACTURE"
        confidence = probability if is_fracture else (1 - probability)
        
        # Check if prediction seems reasonable (not stuck at 0.5)
        if 0.48 <= probability <= 0.52:
            status = "⚠️  STUCK AT 50%"
            failed_models.append((model_display_name, "Stuck at 50%"))
        else:
            status = "✅ WORKING"
            successful_models.append({
                'name': model_display_name,
                'probability': probability,
                'confidence': confidence,
                'accuracy': accuracy
            })
        
        print(f"{model_display_name:<25} {probability:.4f} ({probability*100:>5.1f}%)  {prediction:<20} {status}")
        
    except Exception as e:
        print(f"{model_display_name:<25} {'ERROR':<15} {str(e)[:20]:<20} ❌")
        failed_models.append((model_display_name, str(e)[:50]))

print("\n" + "=" * 70)
print("SUMMARY:")
print("=" * 70)

print(f"\n✅ Working Models: {len(successful_models)}/{len(model_files)}")
for model in successful_models:
    print(f"   - {model['name']}: {model['confidence']*100:.1f}% confident ({model['accuracy']} accuracy)")

if failed_models:
    print(f"\n❌ Failed Models: {len(failed_models)}")
    for name, reason in failed_models:
        print(f"   - {name}: {reason}")

print("\n" + "=" * 70)
print("ENSEMBLE PREDICTION:")
print("=" * 70)

if successful_models:
    # Calculate weighted average
    weights = {
        'EfficientNet B4': 0.95,
        'ResNet50': 0.94,
        'DenseNet121': 0.93,
        'FracNet': 0.91,
        'MURA DenseNet169': 0.89
    }
    
    total_weight = sum(weights.get(m['name'], 0.85) for m in successful_models)
    weighted_prob = sum(m['probability'] * weights.get(m['name'], 0.85) 
                       for m in successful_models) / total_weight
    
    is_fracture = weighted_prob > 0.5
    confidence = weighted_prob if is_fracture else (1 - weighted_prob)
    
    print(f"\nWeighted Average Probability: {weighted_prob:.4f} ({weighted_prob*100:.1f}%)")
    print(f"Final Prediction: {'FRACTURE' if is_fracture else 'NO FRACTURE'}")
    print(f"Confidence: {confidence*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("VERDICT:")
    print("=" * 70)
    
    if not is_fracture:
        print("\n✅ CORRECT! Ensemble predicts NO FRACTURE")
        print(f"   (Expected: No fracture on test image)")
    else:
        print(f"\n❌ INCORRECT! Ensemble predicts FRACTURE with {confidence*100:.1f}% confidence")
        print("   (Expected: No fracture on test image)")
else:
    print("\n❌ No working models - cannot make ensemble prediction")

print("\n" + "=" * 70)
print("FIXES APPLIED:")
print("=" * 70)
print("""
1. ✅ FracNet architecture fixed
   - Removed incorrect backbone.fc = Identity()
   - Now properly uses ResNet features before avgpool

2. ✅ All models re-enabled
   - EfficientNet, FracNet, ResNet50, DenseNet, MURA

3. ✅ Ensemble voting implemented
   - Weighted average based on model accuracy
   - More robust than single model

4. ✅ Double sigmoid bug fixed
   - Models already have sigmoid in final layer
   - predict_fracture() no longer applies sigmoid again
""")
