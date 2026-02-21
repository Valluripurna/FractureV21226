import torch
import torch.nn as nn
import torchvision.models as models
import os
import sys

# Add the parent torchxrayvision directory to the path to allow the unpickler to find the modules
sys.path.insert(0, os.path.abspath('torchxrayvision'))

# Create the models directory if it doesn't exist
models_dir = 'models'
os.makedirs(models_dir, exist_ok=True)

class FracNet(nn.Module):
    """A simplified FracNet-like model for X-ray fracture detection.
    
    This model is inspired by the original FracNet architecture but adapted for X-ray images.
    It uses a ResNet backbone with custom layers for fracture detection.
    """
    
    def __init__(self, num_classes=1):
        super(FracNet, self).__init__()
        
        # Use ResNet50 as the backbone (similar to original FracNet's 3D UNet concept but adapted for 2D)
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

# Create the FracNet model
model = FracNet()

# Define the path to save the model
model_path = os.path.join(models_dir, 'fracnet_model.pth')

# Save the complete model
torch.save(model.state_dict(), model_path)

print(f"FracNet model saved to '{model_path}'")
print(f"Model structure: ResNet50 backbone with custom fracture detection layers")
print(f"Input size: 224x224 RGB images")
print(f"Output: Probability of fracture (0-1)")