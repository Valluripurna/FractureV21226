"""Test script to verify model predictions on sample images."""
import torch
import os
from model import load_model, preprocess_image, predict_fracture

# Check model file sizes
models_dir = os.path.join('..', 'models')
model_files = [
    'resnet50_fracture_model.pth',
    'densenet121_fracture_model.pth', 
    'efficientnet_fracture_model.pth',
    'fracnet_model.pth',
    'mura_model_pytorch.pth'
]

print("=" * 60)
print("MODEL FILE ANALYSIS")
print("=" * 60)

for model_file in model_files:
    path = os.path.join(models_dir, model_file)
    if os.path.exists(path):
        size_kb = os.path.getsize(path) / 1024
        print(f"{model_file:40s} {size_kb:10.1f} KB")
        
        # Check if it's just an empty or dummy model
        if size_kb < 100:  # Less than 100KB is suspicious
            print(f"  ⚠️  WARNING: Very small file size - likely untrained/dummy model")
    else:
        print(f"{model_file:40s} NOT FOUND")

print("\n" + "=" * 60)
print("MODEL LOADING TEST")
print("=" * 60)

# Try loading models and checking their structure
for model_file in model_files[:3]:  # Test first 3 models
    path = os.path.join(models_dir, model_file)
    if os.path.exists(path):
        try:
            print(f"\nLoading {model_file}...")
            model = load_model(path)
            
            # Count parameters
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
            
            print(f"  Total parameters: {total_params:,}")
            print(f"  Trainable parameters: {trainable_params:,}")
            
            # Check if all weights are zeros (untrained)
            all_zero = all(torch.all(p == 0).item() for p in model.parameters())
            if all_zero:
                print(f"  ❌ ERROR: All weights are ZERO - model is UNTRAINED!")
            else:
                print(f"  ✓ Model has non-zero weights")
                
        except Exception as e:
            print(f"  ❌ ERROR loading model: {e}")

print("\n" + "=" * 60)
print("PREDICTION LOGIC TEST")
print("=" * 60)

# Test the sigmoid issue
test_values = [0.5, 0.8, 1.5, 2.0, -1.0, 0.1]
print("\nTesting double sigmoid issue:")
print("Value -> Sigmoid -> Sigmoid Again")
for val in test_values:
    sig1 = torch.sigmoid(torch.tensor(val)).item()
    sig2 = torch.sigmoid(torch.tensor(sig1)).item()
    print(f"{val:6.2f} -> {sig1:.4f} -> {sig2:.4f}")

print("\n⚠️  If model output already has sigmoid, applying it again will")
print("    push all values towards 0.5 (always moderate prediction)!")
