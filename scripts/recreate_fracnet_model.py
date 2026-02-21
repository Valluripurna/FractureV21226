import torch
import torch.nn as nn
import torchvision.models as models
import os

# Define the model class
class FracNetModel(nn.Module):
    """A simplified FracNet-like model for X-ray fracture detection."""
    
    def __init__(self, num_classes=1):
        super(FracNetModel, self).__init__()
        
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

# Create an instance of the model
model = FracNetModel()

# Define the path to save the model
model_path = 'c:/Users/purna/OneDrive/Desktop/Fracture/models/fracnet_model.pth'

# Ensure the directory exists
os.makedirs(os.path.dirname(model_path), exist_ok=True)

# Save the model's state dictionary
torch.save(model.state_dict(), model_path)

print(f"FracNet model saved successfully at {model_path}")
