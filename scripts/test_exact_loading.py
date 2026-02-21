#!/usr/bin/env python3
"""
Test script to replicate exactly what happens in load_model function.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import torch
import torch.nn as nn
import torchvision.models as models
from model import (
    ResNet50FractureModel,
    DenseNetFractureModel,
    EfficientNetFractureModel,
    FracNetModel,
    MURAModel
)

def test_resnet_loading(model_path):
    """Test loading a ResNet model exactly like in load_model function."""
    try:
        print("Creating ResNet50FractureModel...")
        model = ResNet50FractureModel()
        print("✅ Model created successfully")
        
        print("Loading checkpoint with torch.load...")
        checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
        print(f"✅ Checkpoint loaded successfully, type: {type(checkpoint)}")
        
        print("Loading state dict into model...")
        model.load_state_dict(checkpoint, strict=False)
        print("✅ State dict loaded successfully")
        
        return model
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Test loading the resnet50 model exactly as in the app."""
    model_path = "../models/resnet50_fracture_model.pth"
    
    if os.path.exists(model_path):
        print(f"Model file exists: {model_path}")
        model = test_resnet_loading(model_path)
        if model:
            print("✅ Model loaded successfully!")
        else:
            print("❌ Model failed to load")
    else:
        print(f"❌ Model file not found: {model_path}")

if __name__ == "__main__":
    main()