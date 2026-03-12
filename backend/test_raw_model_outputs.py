"""Test raw model outputs to see what's happening with EfficientNet and FracNet."""
import torch
import os
from model import preprocess_image
from torchvision import models
import torch.nn as nn

print("=" * 70)
print("RAW MODEL OUTPUT ANALYSIS")
print("=" * 70)

# Load test image
test_image_path = os.path.join('..', 'test_images', 'test_image.png')

with open(test_image_path, 'rb') as f:
    img_bytes = f.read()

img_tensor = preprocess_image(img_bytes)
print(f"\n✓ Image preprocessed, tensor shape: {img_tensor.shape}")

# Test EfficientNet
print("\n" + "=" * 70)
print("EFFICIENTNET B4 RAW OUTPUT:")
print("=" * 70)

try:
    efficientnet_path = os.path.join('..', 'models', 'efficientnet_fracture_model.pth')
    model_data = torch.load(efficientnet_path, map_location='cpu', weights_only=False)
    
    print(f"\nModel file keys: {list(model_data.keys()) if isinstance(model_data, dict) else 'Not a dict'}")
    
    # Try to load EfficientNet model
    from torchvision.models import efficientnet_b4
    model = efficientnet_b4(weights=None)
    
    # Modify classifier for binary classification
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_features, 1),
        nn.Sigmoid()
    )
    
    # Load state dict
    if isinstance(model_data, dict) and 'model_state_dict' in model_data:
        model.load_state_dict(model_data['model_state_dict'])
    else:
        model.load_state_dict(model_data)
    
    model.eval()
    
    with torch.no_grad():
        raw_output = model(img_tensor)
        print(f"Raw output: {raw_output.item():.6f}")
        print(f"Output shape: {raw_output.shape}")
        
        # Try without final sigmoid
        model_no_sigmoid = efficientnet_b4(weights=None)
        model_no_sigmoid.classifier = nn.Sequential(
            nn.Dropout(p=0.4, inplace=True),
            nn.Linear(in_features, 1)
        )
        
        if isinstance(model_data, dict) and 'model_state_dict' in model_data:
            # Extract weights without sigmoid
            state_dict = model_data['model_state_dict']
            # Try loading (might fail on classifier)
            try:
                model_no_sigmoid.load_state_dict(state_dict, strict=False)
                model_no_sigmoid.eval()
                logit = model_no_sigmoid(img_tensor)
                print(f"Logit (no sigmoid): {logit.item():.6f}")
                manual_sigmoid = torch.sigmoid(logit).item()
                print(f"Manual sigmoid: {manual_sigmoid:.6f}")
            except:
                print("Cannot extract logits")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test FracNet
print("\n" + "=" * 70)
print("FRACNET RAW OUTPUT:")
print("=" * 70)

try:
    fracnet_path = os.path.join('..', 'models', 'fracnet_model.pth')
    model_data = torch.load(fracnet_path, map_location='cpu', weights_only=False)
    
    print(f"\nModel file keys: {list(model_data.keys()) if isinstance(model_data, dict) else 'Not a dict'}")
    
    # Load ResNet50 backbone
    resnet = models.resnet50(weights=None)
    features = nn.Sequential(*list(resnet.children())[:-2])
    
    # Build FracNet
    model = nn.Sequential(
        features,
        nn.AdaptiveAvgPool2d((1, 1)),
        nn.Flatten(),
        nn.Linear(2048, 1),
        nn.Sigmoid()
    )
    
    # Load state dict
    if isinstance(model_data, dict) and 'model_state_dict' in model_data:
        model.load_state_dict(model_data['model_state_dict'])
    else:
        model.load_state_dict(model_data)
    
    model.eval()
    
    with torch.no_grad():
        raw_output = model(img_tensor)
        print(f"Raw output: {raw_output.item():.6f}")
        print(f"Output shape: {raw_output.shape}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test what a completely random/untrained model would output
print("\n" + "=" * 70)
print("CONTROL: RANDOM UNTRAINED MODEL:")
print("=" * 70)

try:
    random_model = nn.Sequential(
        models.resnet50(weights=None),
        nn.Linear(1000, 1),
        nn.Sigmoid()
    )
    random_model.eval()
    
    with torch.no_grad():
        random_output = random_model(img_tensor)
        print(f"Random model output: {random_output.item():.6f}")
        print(f"Expected: ~0.5 (untrained sigmoid defaults to middle)")
        
except Exception as e:
    print(f"❌ Error: {e}")
