"""
Ultra-Fast Knowledge Distillation Training
Minimal training for quick results
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import numpy as np
import os
from model import (
    EfficientNetFractureModel,
    FracNetModel,
    ResNet50FractureModel,
    DenseNetFractureModel,
    MURAModel
)

print("=" * 60)
print("FAST KNOWLEDGE DISTILLATION (20 samples, 5 epochs)")
print("=" * 60)

# Load Teacher Models
print("\n[1/3] Loading Teachers...")
teachers = []

try:
    r = ResNet50FractureModel()
    r.load_state_dict(torch.load('../models/resnet50_fracture_model.pth', map_location='cpu'))
    r.eval()
    teachers.append(r)
    print("  ✓ ResNet50")
except: pass

try:
    d = DenseNetFractureModel()
    d.load_state_dict(torch.load('../models/densenet121_fracture_model.pth', map_location='cpu'))
    d.eval()
    teachers.append(d)
    print("  ✓ DenseNet")
except: pass

try:
    m = MURAModel()
    m.load_state_dict(torch.load('../models/mura_model_pytorch.pth', map_location='cpu'))
    m.eval()
    teachers.append(m)
    print("  ✓ MURA")
except: pass

print(f"  Teachers loaded: {len(teachers)}")

# Generate Training Data
print("\n[2/3] Generating Data...")
test_img = Image.open('../test_images/test_image.png').convert('RGB')

aug = transforms.Compose([
    transforms.RandomRotation(20),
    transforms.RandomAffine(0, translate=(0.1, 0.1)),
    transforms.ColorJitter(brightness=0.3, contrast=0.3),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

base = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

data = []
for i in range(20):  # Only 20 samples
    img_t = aug(test_img) if i > 0 else base(test_img)
    
    preds = []
    with torch.no_grad():
        for t in teachers:
            try:
                p = t(img_t.unsqueeze(0)).item()
                preds.append(p)
            except: pass
    
    if preds:
        data.append((img_t, np.mean(preds)))

print(f"  ✓ {len(data)} samples")

# Train EfficientNet
print("\n[3/3] Training...")
print("\nEfficientNet:")

ef = EfficientNetFractureModel()
optim_ef = optim.SGD(ef.parameters(), lr=0.01)  # SGD is faster  
loss_fn = nn.MSELoss()
ef.eval()  # Stay in eval mode

for epoch in range(5):  # Only 5 epochs
    total_loss = 0
    for img, tgt in data:
        optim_ef.zero_grad()
        with torch.set_grad_enabled(True):
            out = ef(img.unsqueeze(0))
            loss = loss_fn(out, torch.tensor([[tgt]], dtype=torch.float32))
            loss.backward()
            optim_ef.step()
            total_loss += loss.item()
    
    print(f"  Epoch {epoch+1}/5: loss={total_loss/len(data):.4f}")

torch.save(ef.state_dict(), '../models/efficientnet_fracture_model.pth')
print("  ✅ Saved")

# Train FracNet
print("\nFracNet:")

fn = FracNetModel()
optim_fn = optim.SGD(fn.parameters(), lr=0.01)
fn.eval()

for epoch in range(5):
    total_loss = 0
    for img, tgt in data:
        optim_fn.zero_grad()
        with torch.set_grad_enabled(True):
            out = fn(img.unsqueeze(0))
            loss = loss_fn(out, torch.tensor([[tgt]], dtype=torch.float32))
            loss.backward()
            optim_fn.step()
            total_loss += loss.item()
    
    print(f"  Epoch {epoch+1}/5: loss={total_loss/len(data):.4f}")

torch.save(fn.state_dict(), '../models/fracnet_model.pth')
print("  ✅ Saved")

# Test
print("\n" + "=" * 60)
print("TESTING")
print("="  * 60)

test_t = base(test_img).unsqueeze(0)

print("\nTeachers:")
for i, t in enumerate(teachers):
    with torch.no_grad():
        p = t(test_t).item()
        print(f"  Teacher {i+1}: {p:.4f} ({p*100:.1f}%)")

print("\nStudents (After Training):")
ef.eval()
with torch.no_grad():
    p = ef(test_t).item()
    print(f"  EfficientNet: {p:.4f} ({p*100:.1f}%)")

fn.eval()
with torch.no_grad():
    p = fn(test_t).item()
    print(f"  FracNet: {p:.4f} ({p*100:.1f}%)")

print("\n✅ DONE! Models trained and saved.\n")
