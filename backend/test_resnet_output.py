"""Check what ResNet50 backbone outputs when fc is Identity."""
import torch
import torch.nn as nn
import torchvision.models as models

# Create ResNet50 with fc = Identity
resnet = models.resnet50(pretrained=False)
resnet.fc = nn.Identity()

print("ResNet50 architecture with fc=Identity:")
print(resnet)

# Test with dummy input
x = torch.randn(1, 3, 224, 224)
output = resnet(x)

print(f"\nInput shape: {x.shape}")
print(f"Output shape: {output.shape}")
print(f"Output dimensions: {len(output.shape)}")

# Test what happens before avgpool
resnet_no_avg = nn.Sequential(*list(resnet.children())[:-2])
features_4d = resnet_no_avg(x)
print(f"\nBefore avgpool shape: {features_4d.shape}")

# Test avgpool alone
avgpool = nn.AdaptiveAvgPool2d((1, 1))
pooled = avgpool(features_4d)
print(f"After avgpool shape: {pooled.shape}")
flattened = torch.flatten(pooled, 1)
print(f"After flatten shape: {flattened.shape}")
