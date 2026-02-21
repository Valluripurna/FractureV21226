import os
import sys
import torch
from PIL import Image
import numpy as np

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from model import load_model, preprocess_image, predict_fracture
from background_evaluator import evaluate_model

# Define model paths
MODEL_DIR = 'c:/Users/purna/OneDrive/Desktop/Fracture/models'
MODEL_PATHS = {
    'resnet50_fracture_model': os.path.join(MODEL_DIR, 'resnet50_fracture_model.pth'),
    'densenet121_fracture_model': os.path.join(MODEL_DIR, 'densenet121_fracture_model.pth'),
    'efficientnet_fracture_model': os.path.join(MODEL_DIR, 'efficientnet_fracture_model.pth'),
    'fracnet_model': os.path.join(MODEL_DIR, 'fracnet_model.pth'),
    'mura_model_pytorch': os.path.join(MODEL_DIR, 'mura_model_pytorch.pth'),
    'rsna_model': os.path.join(MODEL_DIR, 'rsna_model.pth'),
    'vindr_model': os.path.join(MODEL_DIR, 'vindr_model.pth'),
    'fracture_model': os.path.join(MODEL_DIR, 'fracture_model.pth'),
}

def test_models():
    """Test all models with a sample image."""
    image_path = 'c:/Users/purna/OneDrive/Desktop/Fracture/test_images/test_image.png'
    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    input_tensor = preprocess_image(image_bytes)

    print("--- Model Predictions ---")
    for model_name, model_path in MODEL_PATHS.items():
        print(f"Checking for model: {model_name} at {os.path.abspath(model_path)}")
        if os.path.exists(model_path):
            try:
                model = load_model(model_path)
                probability = predict_fracture(model, input_tensor)
                is_fracture = probability > 0.5
                print(f"Model: {model_name}")
                print(f"  - Prediction: {'Fracture' if is_fracture else 'No Fracture'}")
                print(f"  - Probability: {probability:.4f}")
            except Exception as e:
                print(f"Model: {model_name}")
                print(f"  - Error loading or predicting: {e}")
        else:
            print(f"Model: {model_name}")
            print(f"  - Model file not found.")

    print("\n--- Model Accuracies (Placeholder) ---")
    for model_name in MODEL_PATHS.keys():
        accuracy = evaluate_model(None, model_name)
        print(f"Model: {model_name}")
        print(f"  - Accuracy: {accuracy * 100:.2f}%")


if __name__ == '__main__':
    test_models()
