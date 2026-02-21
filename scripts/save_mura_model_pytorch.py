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

# Load the DenseNet169 model with pre-trained ImageNet weights, excluding the top layer
base_model = models.densenet169(pretrained=True)

# Remove the classifier layer
features = list(base_model.children())[:-1]  # Remove the last layer (classifier)

# Add the custom top layer for binary classification as in the notebook
# Global Average Pooling + Dense layer with sigmoid activation
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

# Create the final model
model = MURAModel(base_model)

# Define the path to save the model
model_path = os.path.join(models_dir, 'mura_model_pytorch.pth')

# Save the complete model
torch.save(model.state_dict(), model_path)

print(f"MURA model (PyTorch version) saved to '{model_path}'")
print(f"Model structure: DenseNet169 backbone with binary classification head")