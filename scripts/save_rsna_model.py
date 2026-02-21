import torch
import os
import sys

# Add the parent torchxrayvision directory to the path to allow the unpickler to find the modules
sys.path.insert(0, os.path.abspath('torchxrayvision'))

import torchxrayvision as xrv

# Define the model and weights name
model_name = 'densenet121-res224-rsna'
weights_name = 'densenet121-res224-rsna'

# Create the models directory if it doesn't exist
models_dir = 'models'
os.makedirs(models_dir, exist_ok=True)

# Load the pre-trained model
model = xrv.models.DenseNet(weights=weights_name)

# Define the path to save the model
model_path = os.path.join(models_dir, 'rsna_model.pth')

# Save the model's state dictionary
torch.save(model.state_dict(), model_path)

print(f"Model '{model_name}' saved to '{model_path}'")
