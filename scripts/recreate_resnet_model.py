import torch
import torch.nn as nn
import torchvision.models as models
import os

# Define the model class
class ResNet50FractureModel(nn.Module):
    def __init__(self):
        super(ResNet50FractureModel, self).__init__()
        # Load pretrained ResNet50
        self.resnet50 = models.resnet50(pretrained=True)
        
        # Get the number of input features for the classifier
        num_ftrs = self.resnet50.fc.in_features
        
        # Replace the final fully connected layer for binary classification
        self.resnet50.fc = nn.Sequential(
            nn.Linear(num_ftrs, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.resnet50(x)

# Create an instance of the model
model = ResNet50FractureModel()

# Define the path to save the model
model_path = 'c:/Users/purna/OneDrive/Desktop/Fracture/models/resnet50_fracture_model.pth'

# Ensure the directory exists
os.makedirs(os.path.dirname(model_path), exist_ok=True)

# Save the model's state dictionary
torch.save(model.state_dict(), model_path)

print(f"ResNet50 fracture model saved successfully at {model_path}")
