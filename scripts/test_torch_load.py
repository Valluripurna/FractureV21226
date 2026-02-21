#!/usr/bin/env python3
"""
Test script to check if PyTorch can load the model files directly.
"""

import torch
import os

def main():
    """Test loading model files with PyTorch directly."""
    model_dir = "../models"
    model_files = [
        "resnet50_fracture_model.pth",
        "densenet121_fracture_model.pth",
        "efficientnet_fracture_model.pth",
        "fracnet_model.pth",
        "mura_model_pytorch.pth"
    ]
    
    print(f"Current directory: {os.getcwd()}")
    
    for model_file in model_files:
        model_path = os.path.join(model_dir, model_file)
        print(f"\nTesting {model_file}")
        print(f"  Path: {model_path}")
        print(f"  Exists: {os.path.exists(model_path)}")
        
        if os.path.exists(model_path):
            try:
                print("  Attempting to load with torch.load...")
                state_dict = torch.load(model_path, map_location=torch.device('cpu'))
                print(f"  ✅ Successfully loaded {model_file}")
                print(f"  Type: {type(state_dict)}")
                if isinstance(state_dict, dict):
                    print(f"  Keys: {len(state_dict.keys())}")
                    if len(state_dict.keys()) > 0:
                        print(f"  First few keys: {list(state_dict.keys())[:5]}")
            except Exception as e:
                print(f"  ❌ Failed to load {model_file}: {str(e)}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    main()