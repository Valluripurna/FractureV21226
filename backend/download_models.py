#!/usr/bin/env python3
"""
Script to download pretrained ResNet50 and DenseNet models for X-ray fracture detection.
"""

import torch
import torchvision.models as models
import os
import requests
from tqdm import tqdm

def download_file(url, filename):
    """Download a file with progress bar."""
    print(f"Downloading {filename}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        
        with open(filename, 'wb') as f, tqdm(
            total=total_size, 
            unit='B', 
            unit_scale=True,
            desc=filename
        ) as pbar:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
                    
        print(f"✅ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to download {filename}: {str(e)}")
        return False

def save_pretrained_model(model, filename):
    """Save a pretrained model's state dict."""
    try:
        torch.save(model.state_dict(), filename)
        print(f"✅ Saved pretrained model to {filename}")
        return True
    except Exception as e:
        print(f"❌ Failed to save model to {filename}: {str(e)}")
        return False

def create_fracture_detection_model(base_model, model_type):
    """Create a fracture detection model by modifying a pretrained model."""
    if model_type == "resnet50":
        # Replace the final fully connected layer for binary classification
        num_features = base_model.fc.in_features
        base_model.fc = torch.nn.Sequential(
            torch.nn.Dropout(0.5),
            torch.nn.Linear(num_features, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 1),
            torch.nn.Sigmoid()
        )
        return base_model
    elif model_type == "densenet121":
        # Replace the final classifier for binary classification
        num_features = base_model.classifier.in_features
        base_model.classifier = torch.nn.Sequential(
            torch.nn.Dropout(0.5),
            torch.nn.Linear(num_features, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(512, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(128, 1),
            torch.nn.Sigmoid()
        )
        return base_model
    return base_model

def main():
    """Main function to download and save pretrained models."""
    # Create models directory if it doesn't exist
    models_dir = "../models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"Created directory: {models_dir}")
    
    print("Starting download of pretrained models...")
    
    # 1. Download pretrained ResNet50 and modify for fracture detection
    print("\n1. Creating and saving pretrained ResNet50 model for fracture detection...")
    try:
        resnet50 = models.resnet50(pretrained=True)
        resnet50_fracture = create_fracture_detection_model(resnet50, "resnet50")
        resnet50_path = os.path.join(models_dir, "resnet50_fracture_model.pth")
        save_pretrained_model(resnet50_fracture, resnet50_path)
    except Exception as e:
        print(f"❌ Failed to create/save ResNet50 model: {str(e)}")
    
    # 2. Download pretrained DenseNet121 and modify for fracture detection
    print("\n2. Creating and saving pretrained DenseNet121 model for fracture detection...")
    try:
        densenet121 = models.densenet121(pretrained=True)
        densenet121_fracture = create_fracture_detection_model(densenet121, "densenet121")
        densenet_path = os.path.join(models_dir, "densenet121_fracture_model.pth")
        save_pretrained_model(densenet121_fracture, densenet_path)
    except Exception as e:
        print(f"❌ Failed to create/save DenseNet121 model: {str(e)}")
    
    # 3. Try to download a specialized fracture detection model from GitHub if available
    print("\n3. Attempting to download specialized fracture detection models...")
    
    # Example specialized models (these URLs would need to be updated with actual model URLs)
    # specialized_models = [
    #     {
    #         "url": "https://github.com/migueleven/bone_fracture_classifier/raw/main/models/model.pth",
    #         "filename": "bone_fracture_resnet50.pth"
    #     }
    # ]
    
    # for model_info in specialized_models:
    #     filepath = os.path.join(models_dir, model_info["filename"])
    #     download_file(model_info["url"], filepath)
    
    print("\n✅ Pretrained model download process completed!")
    print(f"Models saved to: {os.path.abspath(models_dir)}")

if __name__ == "__main__":
    main()