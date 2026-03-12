"""Test model predictions on actual images to verify they work correctly."""
import torch
import os
import sys
from model import load_model, preprocess_image, predict_fracture
from PIL import Image
import io

print("=" * 70)
print("REAL IMAGE PREDICTION TEST")
print("=" * 70)

# Load a model
models_dir = os.path.join('..', 'models')
model_path = os.path.join(models_dir, 'efficientnet_fracture_model.pth')

if os.path.exists(model_path):
    print(f"\nLoading model: efficientnet_fracture_model.pth")
    model = load_model(model_path)
    print("✓ Model loaded successfully")
    
    # Test with a dummy image (since we don't have test images readily available)
    print("\n" + "-" * 70)
    print("Creating test images to verify prediction behavior...")
    print("-" * 70)
    
    # Create different test images
    test_cases = []
    
    # 1. All black image (simulating clear/normal)
    black_img = Image.new('RGB', (224, 224), color=(0, 0, 0))
    test_cases.append(("Black image (normal/clear)", black_img))
    
    # 2. All white image (simulating bright/bone)
    white_img = Image.new('RGB', (224, 224), color=(255, 255, 255))
    test_cases.append(("White image (bright bone)", white_img))
    
    # 3. Gray image (typical X-ray)
    gray_img = Image.new('RGB', (224, 224), color=(128, 128, 128))
    test_cases.append(("Gray image (typical X-ray)", gray_img))
    
    # 4. Random noise image
    import numpy as np
    noise = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    noise_img = Image.fromarray(noise)
    test_cases.append(("Random noise", noise_img))
    
    print("\nRunning predictions:")
    print(f"{'Test Image':<30} {'Probability':<15} {'Prediction':<20}")
    print("-" * 70)
    
    for name, test_img in test_cases:
        # Save to bytes and preprocess
        img_byte_arr = io.BytesIO()
        test_img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Preprocess and predict
        img_tensor = preprocess_image(img_bytes)
        probability = predict_fracture(model, img_tensor)
        
        # Determine prediction
        if probability > 0.5:
            prediction = "FRACTURE"
            confidence = probability
        else:
            prediction = "NO FRACTURE"
            confidence = 1 - probability
        
        print(f"{name:<30} {probability:.4f} ({probability*100:.1f}%)  {prediction} ({confidence*100:.1f}%)")
    
    print("\n" + "=" * 70)
    print("ANALYSIS:")
    print("=" * 70)
    print("\nIf all predictions are around 0.5 (50%), the model is NOT working properly.")
    print("Good predictions should vary from 0.1 to 0.9 depending on the image.")
    print("\nNOTE: These are synthetic test images, not real X-rays.")
    print("Real X-ray predictions may differ significantly.")
    
else:
    print(f"❌ Model file not found: {model_path}")

# Check test_images directory
test_images_dir = os.path.join('..', 'test_images')
if os.path.exists(test_images_dir):
    print(f"\n\n📁 Found test_images directory: {test_images_dir}")
    images = [f for f in os.listdir(test_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if images:
        print(f"   Found {len(images)} images:")
        for img in images[:5]:  # Show first 5
            print(f"   - {img}")
        print("\n   You can test with these real images if needed!")
    else:
        print("   (but it's empty)")
