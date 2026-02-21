#!/usr/bin/env python3
"""
Script to create minimal valid PyTorch model files for testing.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import os

def create_simple_model():
    """Create a simple model for testing."""
    model = nn.Sequential(
        nn.Linear(10, 1),
        nn.Sigmoid()
    )
    return model

def main():
    """Create minimal valid model files."""
    models_dir = "../models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Create a simple model
    model = create_simple_model()
    
    # Model files to create
    model_files = [
        "rsna_model.pth",
        "vindr_model.pth",
        "fracture_model.pth"
    ]
    
    print("Creating minimal valid model files...")
    
    for model_file in model_files:
        model_path = os.path.join(models_dir, model_file)
        try:
            torch.save(model.state_dict(), model_path)
            print(f"✅ Created {model_file}")
        except Exception as e:
            print(f"❌ Failed to create {model_file}: {str(e)}")
    
    print("✅ Model file creation completed!")

if __name__ == "__main__":
    main()