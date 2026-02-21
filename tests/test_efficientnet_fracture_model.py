import torch
import torch.nn as nn
import torchvision.models as models
import os
import sys

# Add the parent torchxrayvision directory to the path to allow the unpickler to find the modules
sys.path.insert(0, os.path.abspath('torchxrayvision'))

def test_efficientnet_fracture_model():
    """Test the EfficientNet fracture detection model"""
    print("Testing EfficientNet fracture detection model...")
    
    try:
        # Load the EfficientNet-B4 model with pre-trained ImageNet weights
        base_model = models.efficientnet_b4(pretrained=True)
        
        # Modify the classifier for binary fracture detection
        # Replace the final classifier layer with a binary classifier
        num_features = base_model.classifier[1].in_features
        base_model.classifier = nn.Sequential(
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(num_features, 1),  # Binary classification (fracture vs no fracture)
            nn.Sigmoid()
        )
        
        # Define the path to the saved model
        model_path = os.path.join('models', 'efficientnet_fracture_model.pth')
        
        # Load the saved state dict
        if os.path.exists(model_path):
            state_dict = torch.load(model_path)
            base_model.load_state_dict(state_dict)
            base_model.eval()
            print(f"EfficientNet fracture detection model loaded successfully from {model_path}")
            print(f"Model structure: EfficientNet-B4 backbone with binary classification head")
            print(f"Input size: 224x224 RGB images")
            print(f"Output: Probability of fracture (0-1)")
            return True
        else:
            print(f"EfficientNet fracture detection model file not found: {model_path}")
            return False
            
    except Exception as e:
        print(f"Error loading EfficientNet fracture detection model: {e}")
        return False

if __name__ == "__main__":
    test_efficientnet_fracture_model()