"""Test with the actual test X-ray image."""
import torch
import os
from model import load_model, preprocess_image, predict_fracture
from PIL import Image

print("=" * 70)
print("TESTING WITH REAL X-RAY IMAGE")
print("=" * 70)

# Load model
models_dir = os.path.join('..', 'models')
test_image_path = os.path.join('..', 'test_images', 'test_image.png')

if os.path.exists(test_image_path):
    print(f"\nFound test image: {test_image_path}")
    
    # Load the image to see what it looks like
    img = Image.open(test_image_path)
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")
    
    # Read as bytes
    with open(test_image_path, 'rb') as f:
        img_bytes = f.read()
    
    print(f"\n{'Model':<40} {'Probability':<15} {'Prediction'}")
    print("-" * 70)
    
    # Test with all available models
    model_files = [
        'efficientnet_fracture_model.pth',
        'resnet50_fracture_model.pth',
        'densenet121_fracture_model.pth',
        'fracnet_model.pth',
    ]
    
    for model_file in model_files:
        model_path = os.path.join(models_dir, model_file)
        if os.path.exists(model_path):
            try:
                model = load_model(model_path)
                img_tensor = preprocess_image(img_bytes)
                probability = predict_fracture(model, img_tensor)
                
                prediction = "FRACTURE" if probability > 0.5 else "NO FRACTURE"
                confidence = probability if probability > 0.5 else (1 - probability)
                
                print(f"{model_file:<40} {probability:.4f} ({probability*100:.1f}%)  {prediction} ({confidence*100:.1f}%)")
                
            except Exception as e:
                print(f"{model_file:<40} ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("VERDICT:")
    print("=" * 70)
    
    print("\n⚠️  If all models predict around 0.5 (50%), they are likely:")
    print("   1. Not properly trained for fracture detection")
    print("   2. Outputting random/baseline predictions")
    print("   3. Need to be retrained with actual labeled X-ray data")
    
else:
    print(f"❌ Test image not found: {test_image_path}")
