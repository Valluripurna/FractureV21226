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

# Define the path to save the model
model_path = os.path.join(models_dir, 'efficientnet_fracture_model.pth')

# Create the complete model with the modified classifier
class EfficientNetFractureModel(nn.Module):
    def __init__(self, base_model):
        super(EfficientNetFractureModel, self).__init__()
        self.model = base_model
    
    def forward(self, x):
        return self.model(x)

# Create the model instance
model = EfficientNetFractureModel(base_model)

# Save the complete model
torch.save(model.state_dict(), model_path)

print(f"EfficientNet fracture detection model saved to '{model_path}'")
print(f"Model structure: EfficientNet-B4 backbone with binary classification head")
print(f"Input size: 224x224 RGB images")
print(f"Output: Probability of fracture (0-1)")