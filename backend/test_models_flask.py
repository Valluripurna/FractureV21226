#!/usr/bin/env python3
"""
Test script to diagnose model loading issues in Flask context.
"""

import os
import sys
from model import load_model

# Define model paths exactly like in app.py
MODEL_DIR = '../models'
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

def main():
    """Test loading models like in Flask app."""
    print(f"Current working directory: {os.getcwd()}")
    
    loaded_models = {}
    
    for model_name, model_path in MODEL_PATHS.items():
        print(f"\nChecking {model_name}")
        print(f"  Path: {model_path}")
        print(f"  Exists: {os.path.exists(model_path)}")
        
        if os.path.exists(model_path):
            try:
                print(f"  Attempting to load...")
                model = load_model(model_path)
                loaded_models[model_name] = model
                print(f"  ✅ Successfully loaded {model_name}")
            except Exception as e:
                print(f"  ❌ Failed to load {model_name}: {str(e)}")
        else:
            print(f"  ⚠️  Model file not found")
    
    print(f"\nTotal models loaded: {len(loaded_models)}")

if __name__ == "__main__":
    main()