import torch
import torch.nn as nn
import torchvision.models as models
import os

# Define the model class
class DenseNetFractureModel(nn.Module):
    def __init__(self):
        super(DenseNetFractureModel, self).__init__()
        # Load pretrained DenseNet121
        self.densenet = models.densenet121(pretrained=True)
        
        # Get the number of input features for the classifier
        num_ftrs = self.densenet.classifier.in_features
        
        # Replace the final fully connected layer for binary classification
        self.densenet.classifier = nn.Sequential(
            nn.Linear(num_ftrs, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.densenet(x)

# Create an instance of the model
model = DenseNetFractureModel()

# Define the path to save the model
model_path = 'c:/Users/purna/OneDrive/Desktop/Fracture/models/densenet121_fracture_model.pth'

# Ensure the directory exists
os.makedirs(os.path.dirname(model_path), exist_ok=True)

# Save the model's state dictionary
torch.save(model.state_dict(), model_path)

print(f"DenseNet121 fracture model saved successfully at {model_path}")
