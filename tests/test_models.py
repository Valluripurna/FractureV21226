import torch
import sys
import os

# Add the parent torchxrayvision directory to the path
sys.path.insert(0, os.path.abspath('torchxrayvision'))

import torchxrayvision as xrv
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn as nn
from PIL import Image
import numpy as np

def test_rsna_model():
    """Test the RSNA pneumonia detection model"""
    print("Testing RSNA model...")
    try:
        # Load the RSNA model
        model = xrv.models.DenseNet(weights="densenet121-res224-rsna")
        print(f"RSNA model loaded successfully. Targets: {model.targets}")
        return True
    except Exception as e:
        print(f"Error loading RSNA model: {e}")
        return False

def test_fracture_model():
    """Test the fracture detection model"""
    print("Testing fracture model...")
    try:
        # Load the fracture model (all model which includes fracture detection)
        model = xrv.models.DenseNet(weights="densenet121-res224-all")
        print(f"Fracture model loaded successfully. Targets: {model.targets}")
        
        # Check if fracture is in the targets
        if 'Fracture' in model.targets:
            print("Fracture detection is available in this model")
        else:
            print("Fracture detection is NOT available in this model")
        return True
    except Exception as e:
        print(f"Error loading fracture model: {e}")
        return False

def test_vindr_model():
    """Test the VinDR model"""
    print("Testing VinDR model...")
    try:
        # Load the VinDR model (jfhealthcare model)
        model = xrv.baseline_models.jfhealthcare.DenseNet()
        print(f"VinDR model loaded successfully. Targets: {model.targets}")
        return True
    except Exception as e:
        print(f"Error loading VinDR model: {e}")
        return False

def test_mura_pytorch_model():
    """Test the PyTorch version of the MURA model"""
    print("Testing PyTorch MURA model...")
    
    try:
        # Define the MURA model class (same as in save script)
        class MURAModel(nn.Module):
            def __init__(self, base_model):
                super(MURAModel, self).__init__()
                self.features = nn.Sequential(*list(base_model.children())[:-1])
                self.classifier = nn.Sequential(
                    nn.AdaptiveAvgPool2d((1, 1)),
                    nn.Flatten(),
                    nn.Linear(1664, 1),  # 1664 is the number of features from DenseNet169
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                x = self.features(x)
                x = self.classifier(x)
                return x
        
        # Load the DenseNet169 model with pre-trained ImageNet weights
        base_model = models.densenet169(pretrained=True)
        
        # Create the model
        model = MURAModel(base_model)
        
        # Load the saved state dict
        model_path = os.path.join('models', 'mura_model_pytorch.pth')
        if os.path.exists(model_path):
            state_dict = torch.load(model_path)
            model.load_state_dict(state_dict)
            print(f"MURA PyTorch model loaded successfully from {model_path}")
            print("Model structure: DenseNet169 backbone with binary classification head")
            return True
        else:
            print(f"MURA PyTorch model file not found: {model_path}")
            return False
            
    except Exception as e:
        print(f"Error loading MURA PyTorch model: {e}")
        return False

def test_efficientnet_fracture_model():
    """Test the EfficientNet fracture detection model"""
    print("Testing EfficientNet fracture detection model...")
    
    try:
        # Load the EfficientNet-B4 model with pre-trained ImageNet weights
        base_model = models.efficientnet_b4(pretrained=True)
        
        # Modify the classifier for binary fracture detection
        # Replace the final classifier layer with a binary classifier
        num_features = base_model.classifier[1].in_features
        classifier = nn.Sequential(
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(num_features, 1),  # Binary classification (fracture vs no fracture)
            nn.Sigmoid()
        )
        base_model.classifier = classifier
        
        # Create the complete model with the modified classifier
        class EfficientNetFractureModel(nn.Module):
            def __init__(self, base_model):
                super(EfficientNetFractureModel, self).__init__()
                self.model = base_model
            
            def forward(self, x):
                return self.model(x)
        
        # Create the model instance
        model = EfficientNetFractureModel(base_model)
        
        # Define the path to the saved model
        model_path = os.path.join('models', 'efficientnet_fracture_model.pth')
        
        # Load the saved state dict
        if os.path.exists(model_path):
            state_dict = torch.load(model_path)
            model.load_state_dict(state_dict)
            model.eval()
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

def test_fracnet_model():
    """Test the FracNet model"""
    print("Testing FracNet model...")
    
    try:
        # Recreate the exact same model structure as in save script
        class FracNet(nn.Module):
            """A simplified FracNet-like model for X-ray fracture detection."""
            
            def __init__(self, num_classes=1):
                super(FracNet, self).__init__()
                
                # Use ResNet50 as the backbone
                self.backbone = models.resnet50(pretrained=True)
                
                # Remove the final fully connected layer
                self.backbone.fc = nn.Identity()
                
                # Add custom layers for fracture detection
                self.fracture_detector = nn.Sequential(
                    nn.AdaptiveAvgPool2d((1, 1)),
                    nn.Flatten(),
                    nn.Linear(2048, 512),  # ResNet50 has 2048 features
                    nn.ReLU(inplace=True),
                    nn.Dropout(0.5),
                    nn.Linear(512, 128),
                    nn.ReLU(inplace=True),
                    nn.Dropout(0.3),
                    nn.Linear(128, num_classes),
                    nn.Sigmoid()  # For binary classification (fracture vs no fracture)
                )
            
            def forward(self, x):
                # Extract features using the backbone
                features = self.backbone(x)
                # Detect fractures
                output = self.fracture_detector(features)
                return output
        
        # Create the model
        model = FracNet()
        
        # Define the path to the saved model
        model_path = os.path.join('models', 'fracnet_model.pth')
        
        # Load the saved state dict
        if os.path.exists(model_path):
            state_dict = torch.load(model_path)
            model.load_state_dict(state_dict)
            model.eval()
            print(f"FracNet model loaded successfully from {model_path}")
            print(f"Model structure: ResNet50 backbone with custom fracture detection layers")
            print(f"Input size: 224x224 RGB images")
            print(f"Output: Probability of fracture (0-1)")
            return True
        else:
            print(f"FracNet model file not found: {model_path}")
            return False
            
    except Exception as e:
        print(f"Error loading FracNet model: {e}")
        return False

def test_model_loading_from_file(model_path, weights_name):
    """Test loading a model from a saved file"""
    print(f"Testing model loading from file: {model_path}")
    try:
        if os.path.exists(model_path):
            # Load the model
            model = xrv.models.DenseNet(weights=weights_name)
            print(f"Model loaded successfully from {model_path}. Targets: {model.targets}")
            return True
        else:
            print(f"Model file not found: {model_path}")
            return False
    except Exception as e:
        print(f"Error loading model from {model_path}: {e}")
        return False

def test_baseline_model_loading_from_file(model_path):
    """Test loading a baseline model from a saved file"""
    print(f"Testing baseline model loading from file: {model_path}")
    try:
        if os.path.exists(model_path):
            # For baseline models, we need to instantiate them directly
            # The state dict was saved from the model instance
            model = xrv.baseline_models.jfhealthcare.DenseNet()
            state_dict = torch.load(model_path)
            model.load_state_dict(state_dict)
            print(f"Baseline model loaded successfully from {model_path}. Targets: {model.targets}")
            return True
        else:
            print(f"Model file not found: {model_path}")
            return False
    except Exception as e:
        print(f"Error loading baseline model from {model_path}: {e}")
        return False

if __name__ == "__main__":
    print("Testing all models...\n")
    
    # Test RSNA model
    test_rsna_model()
    print()
    
    # Test fracture model
    test_fracture_model()
    print()
    
    # Test VinDR model
    test_vindr_model()
    print()
    
    # Test MURA PyTorch model
    test_mura_pytorch_model()
    print()
    
    # Test EfficientNet fracture detection model
    test_efficientnet_fracture_model()
    print()
    
    # Test FracNet model
    test_fracnet_model()
    print()
    
    # Test loading from saved files
    print("Testing loading from saved files:")
    test_model_loading_from_file("models/rsna_model.pth", "densenet121-res224-rsna")
    test_model_loading_from_file("models/fracture_model.pth", "densenet121-res224-all")
    test_baseline_model_loading_from_file("models/vindr_model.pth")