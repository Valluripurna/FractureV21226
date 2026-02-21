#!/usr/bin/env python3
"""
Test script to diagnose model loading issues.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from model import load_model

def main():
    """Test loading a specific model."""
    model_path = "../models/resnet50_fracture_model.pth"
    
    if os.path.exists(model_path):
        print(f"Model file exists: {model_path}")
        try:
            print("Attempting to load model...")
            model = load_model(model_path)
            print("✅ Model loaded successfully!")
            print(f"Model type: {type(model)}")
        except Exception as e:
            print(f"❌ Failed to load model: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Model file not found: {model_path}")

if __name__ == "__main__":
    main()