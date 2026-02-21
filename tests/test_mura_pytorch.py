import torch
import torch.nn as nn
import torchvision.models as models
import os
import sys

# Add the parent torchxrayvision directory to the path to allow the unpickler to find the modules
sys.path.insert(0, os.path.abspath('torchxrayvision'))

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

if __name__ == "__main__":
    test_mura_pytorch_model()