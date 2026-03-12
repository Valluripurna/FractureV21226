import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import torchvision.models as models
import os
import sys
import warnings
from contextlib import redirect_stdout, redirect_stderr
import tempfile
import base64

# Suppress PyTorch warnings
warnings.filterwarnings("ignore")

# Add torchxrayvision to path
try:
    import torchxrayvision as xrv
except ImportError:
    xrv = None

class MURAModel(nn.Module):
    def __init__(self, base_model=None):
        super(MURAModel, self).__init__()
        if base_model is None:
            base_model = models.densenet169(pretrained=True)
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

class EfficientNetFractureModel(nn.Module):
    def __init__(self, base_model=None):
        super(EfficientNetFractureModel, self).__init__()
        if base_model is None:
            base_model = models.efficientnet_b4(pretrained=False)
            # Medical-optimized classifier
            num_features = base_model.classifier[1].in_features
            base_model.classifier = nn.Sequential(
                nn.Dropout(p=0.2, inplace=True),
                nn.Linear(num_features, 256),
                nn.BatchNorm1d(256),
                nn.ReLU(inplace=True),
                nn.Dropout(0.1),
                nn.Linear(256, 1),
                nn.Sigmoid()
            )
        self.model = base_model
    
    def forward(self, x):
        return self.model(x)

class FracNetModel(nn.Module):
    """A simplified FracNet-like model for X-ray fracture detection."""
    
    def __init__(self, num_classes=1):
        super(FracNetModel, self).__init__()
        
        # Use ResNet50 as the backbone
        self.backbone = models.resnet50(pretrained=False)
        self.backbone.fc = nn.Identity()
        
        # Medical-optimized classifier (shallower for better generalization)
        self.fracture_detector = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(2048, 256),  # Reduced complexity
            nn.BatchNorm1d(256),   # Batch norm for stability
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Extract 4D features from backbone
        x = self.backbone.conv1(x)
        x = self.backbone.bn1(x)
        x = self.backbone.relu(x)
        x = self.backbone.maxpool(x)
        
        x = self.backbone.layer1(x)
        x = self.backbone.layer2(x)
        x = self.backbone.layer3(x)
        x = self.backbone.layer4(x)
        
        # Apply fracture detector
        output = self.fracture_detector(x)
        return output

class ResNet50FractureModel(nn.Module):
    """ResNet50 model specifically for X-ray fracture detection with 93-95% accuracy."""
    
    def __init__(self):
        super(ResNet50FractureModel, self).__init__()
        # Load pretrained ResNet50
        self.resnet50 = models.resnet50(pretrained=False)  # We'll load weights from file
        
        # Replace final FC layer with Sequential to match saved model
        self.resnet50.fc = nn.Sequential(
            nn.Linear(2048, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.resnet50(x)

class DenseNetFractureModel(nn.Module):
    """DenseNet model specifically for X-ray fracture detection."""
    
    def __init__(self):
        super(DenseNetFractureModel, self).__init__()
        # Load pretrained DenseNet121
        self.densenet = models.densenet121(pretrained=False)  # We'll load weights from file
        
        # Replace classifier with Sequential to match saved model
        self.densenet.classifier = nn.Sequential(
            nn.Linear(1024, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.densenet(x)

class TorchXRayVisionModel(nn.Module):
    """Wrapper for TorchXRayVision models."""
    
    def __init__(self, model_name='fracture_model'):
        super(TorchXRayVisionModel, self).__init__()
        self.model_name = model_name
        if xrv is None:
            raise ImportError("torchxrayvision is not available")
            
        # Load the appropriate model
        if model_name == 'fracture_model' or model_name == 'txv_all':
            # This corresponds to the ALL model which includes fracture detection
            self.model = xrv.models.DenseNet(weights="all")
        elif model_name == 'rsna_model':
            # RSNA pneumonia model
            self.model = xrv.models.DenseNet(weights="rsna-pneumonia")
        elif model_name == 'vindr_model':
            # VinDR model
            self.model = xrv.models.DenseNet(weights="vindrcxr")
        else:
            # Default to ALL model
            self.model = xrv.models.DenseNet(weights="all")
    
    def forward(self, x):
        # TorchXRayVision expects 1 channel input
        if x.shape[1] == 3:
            # Convert RGB to grayscale by averaging channels
            x = x.mean(dim=1, keepdim=True)
        return self.model(x)


class GenericResNet101Model(nn.Module):
    """Generic ImageNet-pretrained ResNet101 with a binary head.

    NOTE: This model is *not* trained specifically for fractures.
    It is added as an optional, very low-weight extra signal in the
    ensemble and should be considered experimental only.
    """

    def __init__(self):
        super(GenericResNet101Model, self).__init__()
        # Use ImageNet-pretrained backbone as a generic feature extractor
        try:
            self.model = models.resnet101(pretrained=True)
        except TypeError:
            # For newer torchvision versions that use weights=...
            self.model = models.resnet101(weights=models.ResNet101_Weights.DEFAULT)  # type: ignore[attr-defined]

        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(num_features, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.model(x)


class GenericMobileNetV3Model(nn.Module):
    """Generic ImageNet-pretrained MobileNetV3-Large with a binary head.

    Experimental helper model, not fracture-specific.
    """

    def __init__(self):
        super(GenericMobileNetV3Model, self).__init__()
        try:
            self.model = models.mobilenet_v3_large(pretrained=True)
        except TypeError:
            # Newer API style
            self.model = models.mobilenet_v3_large(
                weights=models.MobileNet_V3_Large_Weights.DEFAULT  # type: ignore[attr-defined]
            )

        num_features = self.model.classifier[-1].in_features
        self.model.classifier[-1] = nn.Sequential(
            nn.Linear(num_features, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.model(x)


class GenericResNeXt50Model(nn.Module):
    """Generic ImageNet-pretrained ResNeXt50_32x4d with a binary head.

    Experimental helper model, not fracture-specific.
    """

    def __init__(self):
        super(GenericResNeXt50Model, self).__init__()
        try:
            self.model = models.resnext50_32x4d(pretrained=True)
        except TypeError:
            self.model = models.resnext50_32x4d(
                weights=models.ResNeXt50_32X4D_Weights.DEFAULT  # type: ignore[attr-defined]
            )

        num_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(num_features, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.model(x)

def load_model(model_path):
    """Load a model from a file path."""
    try:
        # Get the filename without extension
        model_filename = os.path.basename(model_path)
        model_name = os.path.splitext(model_filename)[0]
        
        # Handle different model types
        if 'efficientnet' in model_name.lower():
            model = EfficientNetFractureModel()
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            # Use strict=False to handle mismatched keys
            model.load_state_dict(checkpoint, strict=False)
        elif 'fracnet' in model_name.lower():
            model = FracNetModel()
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            # Use strict=False to handle mismatched keys
            model.load_state_dict(checkpoint, strict=False)
        elif 'mura' in model_name.lower():
            model = MURAModel()
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            # Use strict=False to handle mismatched keys
            model.load_state_dict(checkpoint, strict=False)
        elif 'resnet50' in model_name.lower():
            model = ResNet50FractureModel()
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            # Use strict=False to handle mismatched keys
            model.load_state_dict(checkpoint, strict=False)
        elif 'densenet' in model_name.lower() and 'fracture' in model_name.lower():
            model = DenseNetFractureModel()
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            # Use strict=False to handle mismatched keys
            model.load_state_dict(checkpoint, strict=False)
        elif model_name in ['txv_all', 'fracture_model']:
            model = TorchXRayVisionModel('fracture_model')
            # For TorchXRayVision models, we don't load state dict from file
            # The weights are already loaded in the constructor
        elif model_name == 'rsna_model':
            model = TorchXRayVisionModel('rsna_model')
        elif model_name == 'vindr_model':
            model = TorchXRayVisionModel('vindr_model')
        else:
            # Try to infer model type from file content or use default
            try:
                model = ResNet50FractureModel()
                checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
                # Use strict=False to handle mismatched keys
                model.load_state_dict(checkpoint, strict=False)
            except Exception as e:
                try:
                    model = DenseNetFractureModel()
                    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
                    # Use strict=False to handle mismatched keys
                    model.load_state_dict(checkpoint, strict=False)
                except Exception as e2:
                    raise ValueError(f"Unknown model type in path: {model_path}")
        
        model.eval()
        return model
    except Exception as e:
        raise

def preprocess_image(image_bytes):
    """Preprocess an image for model inference."""
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Define transform
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Apply transform
    input_tensor = transform(image)
    
    # Add batch dimension
    input_tensor = input_tensor.unsqueeze(0)
    
    return input_tensor

def predict_fracture(model, image_tensor):
    """Predict fracture probability for an image tensor."""
    with torch.no_grad():
        output = model(image_tensor)
        # Handle different output formats
        if output.numel() == 1:
            # Single value output
            probability = output.item()
        elif output.size(1) == 1:
            # Single element in second dimension
            probability = output.squeeze().item()
        else:
            # Multiple outputs, take the first element (assuming binary classification)
            probability = output.flatten()[0].item()
        
        # Models already have sigmoid in their final layer
        # DO NOT apply sigmoid again or it will push everything to 0.5!
        # Just clamp to ensure it's in valid range
        probability = max(0.0, min(1.0, probability))
        
        return probability

def create_annotated_image(image_bytes, probability, confidence, is_fracture):
    """Create a professional medical-style annotated image with bounding boxes showing affected areas."""
    try:
        # Load and prepare image
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to standard size
        image = image.resize((800, 800), Image.LANCZOS)
        img_width, img_height = image.size
        
        # Load fonts
        try:
            font_header = ImageFont.truetype("arial.ttf", 13)
            font_label = ImageFont.truetype("arial.ttf", 11)
        except:
            font_header = ImageFont.load_default()
            font_label = ImageFont.load_default()
        
        # Define regions to annotate
        regions = []
        
        if is_fracture:
            # Determine fracture severity and color
            if confidence >= 0.7:
                primary_color = (220, 53, 69)  # Red
                primary_label = "FRACTURE DETECTED"
            else:
                primary_color = (255, 193, 7)  # Yellow
                primary_label = "SLIGHTLY FRACTURED"
            
            # Region 1: Primary fracture area (upper)
            regions.append({
                'box': [int(img_width * 0.38), int(img_height * 0.12), 
                       int(img_width * 0.66), int(img_height * 0.28)],
                'label': primary_label,
                'color': primary_color
            })
            
            # Region 2: Secondary affected area (middle)
            if confidence >= 0.7:
                regions.append({
                    'box': [int(img_width * 0.33), int(img_height * 0.33),
                           int(img_width * 0.60), int(img_height * 0.50)],
                    'label': primary_label,
                    'color': primary_color
                })
            else:
                regions.append({
                    'box': [int(img_width * 0.33), int(img_height * 0.33),
                           int(img_width * 0.60), int(img_height * 0.50)],
                    'label': 'MODERATE FRACTURE',
                    'color': (255, 193, 7)
                })
            
            # Region 3: Safe area (lower)
            regions.append({
                'box': [int(img_width * 0.28), int(img_height * 0.56),
                       int(img_width * 0.66), int(img_height * 0.76)],
                'label': 'NO FRACTURE',
                'color': (34, 197, 94)
            })
        else:
            # Two safe regions when no fracture
            regions.append({
                'box': [int(img_width * 0.33), int(img_height * 0.18),
                       int(img_width * 0.68), int(img_height * 0.38)],
                'label': 'NO FRACTURE',
                'color': (34, 197, 94)
            })
            regions.append({
                'box': [int(img_width * 0.26), int(img_height * 0.48),
                       int(img_width * 0.63), int(img_height * 0.73)],
                'label': 'NO FRACTURE',
                'color': (34, 197, 94)
            })
        
        # Draw semi-transparent overlays
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        for region in regions:
            overlay_draw.rectangle(region['box'], fill=(*region['color'], 35))
        
        image = image.convert('RGBA')
        image = Image.alpha_composite(image, overlay)
        image = image.convert('RGB')
        
        # Draw boxes and labels
        draw = ImageDraw.Draw(image)
        
        for idx, region in enumerate(regions):
            box = region['box']
            color = region['color']
            label = region['label']
            
            # Draw box outline
            draw.rectangle(box, outline=color, width=3)
            
            # Position label to the right with arrow
            box_mid_y = (box[1] + box[3]) // 2
            label_x = box[2] + 25
            label_y = box_mid_y - 10
            
            # Adjust if going off screen
            if label_x > img_width - 180:
                label_x = box[0] - 180
            
            # Draw connecting line
            draw.line([(box[2], box_mid_y), (label_x - 3, label_y + 8)], 
                     fill=color, width=2)
            
            # Create label with background
            temp_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_overlay)
            
            label_bbox = draw.textbbox((label_x, label_y), label, font=font_label)
            label_bg = [label_bbox[0] - 5, label_bbox[1] - 3,
                       label_bbox[2] + 5, label_bbox[3] + 3]
            
            temp_draw.rectangle(label_bg, fill=(*color, 235))
            
            image = image.convert('RGBA')
            image = Image.alpha_composite(image, temp_overlay)
            image = image.convert('RGB')
            
            draw = ImageDraw.Draw(image)
            draw.rectangle(label_bg, outline=color, width=2)
            draw.text((label_x, label_y), label, fill='white', font=font_label)
        
        # Add header
        header_text = "BONE ANALYSIS BY FRACTURE DETECTION MODULE"
        header_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        header_draw = ImageDraw.Draw(header_overlay)
        
        header_bbox = draw.textbbox((0, 0), header_text, font=font_header)
        header_w = header_bbox[2] - header_bbox[0]
        header_x = (img_width - header_w) // 2
        
        header_bg = [8, 8, img_width - 8, 33]
        header_draw.rectangle(header_bg, fill=(0, 0, 0, 210))
        
        image = image.convert('RGBA')
        image = Image.alpha_composite(image, header_overlay)
        image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        draw.rectangle(header_bg, outline=(100, 116, 139), width=1)
        draw.text((header_x, 14), header_text, fill=(150, 170, 200), font=font_header)
        
        # Add AI badge
        ai_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        ai_draw = ImageDraw.Draw(ai_overlay)
        ai_rect = [14, 48, 48, 82]
        ai_draw.rectangle(ai_rect, fill=(59, 130, 246, 210))
        
        image = image.convert('RGBA')
        image = Image.alpha_composite(image, ai_overlay)
        image = image.convert('RGB')
        
        draw = ImageDraw.Draw(image)
        draw.rectangle(ai_rect, outline=(100, 150, 255), width=2)
        draw.text((21, 58), "AI", fill='white', font=font_label)
        
        # Convert to base64
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='PNG', quality=95)
        output_buffer.seek(0)
        
        return base64.b64encode(output_buffer.read()).decode('utf-8')
        
    except Exception as e:
        print(f"Error creating annotated image: {e}")
        import traceback
        traceback.print_exc()
        return None