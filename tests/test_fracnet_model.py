import torch
import torch.nn as nn
import torchvision.models as models
import os
import sys

# Add the parent torchxrayvision directory to the path to allow the unpickler to find the modules
sys.path.insert(0, os.path.abspath('torchxrayvision'))

def test_fracnet_model():
    """Test the FracNet model"""
    print("Testing FracNet model...")
    
    try:
        # Define the FracNet model class (same as in save script)
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

if __name__ == "__main__":
    test_fracnet_model()