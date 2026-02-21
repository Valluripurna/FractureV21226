"""
Script to compare model accuracy on unseen X-ray images.
This script loads all available models and evaluates their performance on a test dataset.
"""

import torch
import torch.nn as nn
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import os
import sys
import json
from tqdm import tqdm

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'torchxrayvision'))

try:
    import torchxrayvision as xrv
except ImportError:
    print("Warning: torchxrayvision not available")

# Import model classes from backend
from model import (
    EfficientNetFractureModel, 
    FracNetModel, 
    TorchXRayVisionModel, 
    MURAModel,
    RSNAModel,
    VinDRModel
)

def load_image(image_path, model_type='rgb'):
    """
    Load and preprocess an X-ray image for model inference.
    
    Args:
        image_path (str): Path to the X-ray image
        model_type (str): Type of preprocessing ('rgb', 'grayscale', 'vindr')
    
    Returns:
        torch.Tensor: Preprocessed image tensor
    """
    # Load image
    image = Image.open(image_path)
    
    if model_type == 'grayscale':
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        # Resize to 224x224
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
        image_tensor = transform(image)
        # Add channel dimension if needed
        if len(image_tensor.shape) == 3:
            image_tensor = image_tensor.mean(dim=0, keepdim=True)
        else:
            image_tensor = image_tensor.unsqueeze(0)
    elif model_type == 'vindr':
        # VinDR model preprocessing (512x512 grayscale)
        if image.mode != 'L':
            image = image.convert('L')
        transform = transforms.Compose([
            transforms.Resize((512, 512)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5], std=[0.5])
        ])
        image_tensor = transform(image).unsqueeze(0)
    else:  # rgb
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        # Resize to 224x224
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        image_tensor = transform(image).unsqueeze(0)
    
    return image_tensor

def load_all_models():
    """
    Load all available models.
    
    Returns:
        dict: Dictionary mapping model names to model instances and preprocessing types
    """
    models = {}
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    
    # Load EfficientNet-B4 Fracture Detection Model
    try:
        efficientnet_model = EfficientNetFractureModel()
        efficientnet_path = os.path.join(model_dir, 'efficientnet_fracture_model.pth')
        if os.path.exists(efficientnet_path):
            efficientnet_model.load_state_dict(torch.load(efficientnet_path, map_location=torch.device('cpu')))
            efficientnet_model.eval()
            models['EfficientNet-B4 Fracture Model'] = {
                'model': efficientnet_model,
                'type': 'rgb',
                'fracture_capable': True
            }
            print(f"Loaded EfficientNet-B4 Fracture Model")
        else:
            print(f"Warning: {efficientnet_path} not found")
    except Exception as e:
        print(f"Warning: Could not load EfficientNet-B4 Fracture Model: {e}")
    
    # Load FracNet Model
    try:
        fracnet_model = FracNetModel()
        fracnet_path = os.path.join(model_dir, 'fracnet_model.pth')
        if os.path.exists(fracnet_path):
            fracnet_model.load_state_dict(torch.load(fracnet_path, map_location=torch.device('cpu')))
            fracnet_model.eval()
            models['FracNet Model'] = {
                'model': fracnet_model,
                'type': 'rgb',
                'fracture_capable': True
            }
            print(f"Loaded FracNet Model")
        else:
            print(f"Warning: {fracnet_path} not found")
    except Exception as e:
        print(f"Warning: Could not load FracNet Model: {e}")
    
    # Load TorchXRayVision ALL Model
    try:
        txv_all_model = TorchXRayVisionModel(model_name='fracture_model')
        txv_all_path = os.path.join(model_dir, 'fracture_model.pth')
        if os.path.exists(txv_all_path):
            txv_all_model.load_state_dict(torch.load(txv_all_path, map_location=torch.device('cpu')))
            txv_all_model.eval()
            models['TorchXRayVision ALL Model'] = {
                'model': txv_all_model,
                'type': 'grayscale',
                'fracture_capable': True
            }
            print(f"Loaded TorchXRayVision ALL Model")
        else:
            print(f"Warning: {txv_all_path} not found")
    except Exception as e:
        print(f"Warning: Could not load TorchXRayVision ALL Model: {e}")
    
    # Load MURA Model
    try:
        mura_model = MURAModel()
        mura_path = os.path.join(model_dir, 'mura_model_pytorch.pth')
        if os.path.exists(mura_path):
            mura_model.load_state_dict(torch.load(mura_path, map_location=torch.device('cpu')))
            mura_model.eval()
            models['MURA Model'] = {
                'model': mura_model,
                'type': 'rgb',
                'fracture_capable': True
            }
            print(f"Loaded MURA Model")
        else:
            print(f"Warning: {mura_path} not found")
    except Exception as e:
        print(f"Warning: Could not load MURA Model: {e}")
    
    # Load RSNA Model
    try:
        rsna_model = RSNAModel()
        rsna_path = os.path.join(model_dir, 'rsna_model.pth')
        if os.path.exists(rsna_path):
            rsna_model.load_state_dict(torch.load(rsna_path, map_location=torch.device('cpu')))
            rsna_model.eval()
            models['RSNA Model'] = {
                'model': rsna_model,
                'type': 'grayscale',
                'fracture_capable': False  # Not fracture capable
            }
            print(f"Loaded RSNA Model")
        else:
            print(f"Warning: {rsna_path} not found")
    except Exception as e:
        print(f"Warning: Could not load RSNA Model: {e}")
    
    # Load VinDR Model
    try:
        vindr_model = VinDRModel()
        vindr_path = os.path.join(model_dir, 'vindr_model.pth')
        if os.path.exists(vindr_path):
            vindr_model.load_state_dict(torch.load(vindr_path, map_location=torch.device('cpu')))
            vindr_model.eval()
            models['VinDR Model'] = {
                'model': vindr_model,
                'type': 'vindr',
                'fracture_capable': False  # Not fracture capable
            }
            print(f"Loaded VinDR Model")
        else:
            print(f"Warning: {vindr_path} not found")
    except Exception as e:
        print(f"Warning: Could not load VinDR Model: {e}")
    
    return models

def predict_single_image(model_info, image_tensor):
    """
    Make a prediction on a single image using a specific model.
    
    Args:
        model_info (dict): Model information containing model instance and metadata
        image_tensor (torch.Tensor): Preprocessed image tensor
    
    Returns:
        float: Prediction probability (0-1)
    """
    model = model_info['model']
    try:
        with torch.no_grad():
            output = model(image_tensor)
            
            # Handle different output formats
            if isinstance(output, tuple) or isinstance(output, list):
                # For models that return multiple outputs
                output = output[0]
            
            # Apply sigmoid if needed (for binary classification)
            if torch.all(output >= 0) and torch.all(output <= 1):
                # Already sigmoid applied
                prediction = output.item() if output.numel() == 1 else output.flatten()[15].item()  # Fracture index
            else:
                # Apply sigmoid
                prediction = torch.sigmoid(output).item() if output.numel() == 1 else torch.sigmoid(output).flatten()[15].item()
                
            return float(prediction)
    except Exception as e:
        print(f"Warning: Prediction error for model: {e}")
        return 0.0

def evaluate_models_on_dataset(models, image_dir, ground_truth_file=None):
    """
    Evaluate all models on a dataset of X-ray images.
    
    Args:
        models (dict): Dictionary of loaded models
        image_dir (str): Directory containing X-ray images
        ground_truth_file (str): Optional JSON file with ground truth labels
    
    Returns:
        dict: Evaluation results for each model
    """
    if not os.path.exists(image_dir):
        print(f"Error: Image directory {image_dir} not found")
        return {}
    
    # Get list of image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    image_files = [f for f in os.listdir(image_dir) 
                   if os.path.splitext(f)[1].lower() in image_extensions]
    
    if not image_files:
        print(f"No image files found in {image_dir}")
        return {}
    
    print(f"Found {len(image_files)} images for evaluation")
    
    # Load ground truth if provided
    ground_truth = {}
    if ground_truth_file and os.path.exists(ground_truth_file):
        try:
            with open(ground_truth_file, 'r') as f:
                ground_truth = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load ground truth file: {e}")
    
    # Initialize results dictionary
    results = {name: {
        'predictions': [],
        'ground_truth': [],
        'correct': 0,
        'total': 0,
        'accuracy': 0.0,
        'fracture_capable': info['fracture_capable']
    } for name, info in models.items()}
    
    # Process each image
    print("Evaluating models on images...")
    for image_file in tqdm(image_files):
        image_path = os.path.join(image_dir, image_file)
        
        try:
            # Get ground truth if available
            true_label = None
            if image_file in ground_truth:
                true_label = ground_truth[image_file]
            elif ground_truth:
                # Try without extension
                name_without_ext = os.path.splitext(image_file)[0]
                if name_without_ext in ground_truth:
                    true_label = ground_truth[name_without_ext]
            
            # Process with each model
            for model_name, model_info in models.items():
                # Load and preprocess image
                image_tensor = load_image(image_path, model_info['type'])
                
                # Make prediction
                prediction = predict_single_image(model_info, image_tensor)
                
                # Store prediction
                results[model_name]['predictions'].append({
                    'image': image_file,
                    'prediction': prediction,
                    'predicted_class': 'fracture' if prediction > 0.5 else 'normal'
                })
                
                # Compare with ground truth if available
                if true_label is not None:
                    results[model_name]['ground_truth'].append(true_label)
                    predicted_class = 1 if prediction > 0.5 else 0
                    if predicted_class == true_label:
                        results[model_name]['correct'] += 1
                    results[model_name]['total'] += 1
        
        except Exception as e:
            print(f"Warning: Error processing {image_file}: {e}")
            continue
    
    # Calculate accuracies
    for model_name, result in results.items():
        if result['total'] > 0:
            result['accuracy'] = result['correct'] / result['total']
        else:
            # If no ground truth, we can't calculate accuracy
            result['accuracy'] = None
    
    return results

def find_best_model(results):
    """
    Find the model with the highest accuracy.
    
    Args:
        results (dict): Evaluation results for each model
    
    Returns:
        tuple: (best_model_name, best_accuracy, results_summary)
    """
    best_model = None
    best_accuracy = -1
    fracture_models = []
    
    # Prepare results summary
    summary = []
    for model_name, result in results.items():
        accuracy = result['accuracy']
        fracture_capable = result['fracture_capable']
        
        if fracture_capable:
            fracture_models.append(model_name)
        
        if accuracy is not None and accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model = model_name
            
        summary.append({
            'model': model_name,
            'accuracy': accuracy,
            'fracture_capable': fracture_capable,
            'total_predictions': len(result['predictions'])
        })
    
    return best_model, best_accuracy, summary

def main():
    """
    Main function to compare model accuracy on unseen X-ray images.
    """
    print("=== Bone Fracture Detection Model Comparison ===")
    
    # Load all models
    print("\nLoading models...")
    models = load_all_models()
    
    if not models:
        print("Error: No models could be loaded")
        return
    
    print(f"\nSuccessfully loaded {len(models)} models")
    
    # Define image directory (user needs to place images here)
    image_dir = os.path.join(os.path.dirname(__file__), '..', 'test_images')
    
    # Create test_images directory if it doesn't exist
    if not os.path.exists(image_dir):
        print(f"\nCreating {image_dir} directory for test images")
        os.makedirs(image_dir)
        print("Please place your unseen X-ray images in the 'test_images' directory and run this script again.")
        return
    
    # Check if directory has images
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']
    image_files = [f for f in os.listdir(image_dir) 
                   if os.path.splitext(f)[1].lower() in image_extensions]
    
    if not image_files:
        print(f"\nThe 'test_images' directory is empty.")
        print("Please place your unseen X-ray images in the 'test_images' directory and run this script again.")
        return
    
    print(f"\nFound {len(image_files)} images for evaluation")
    
    # Evaluate models
    print("\nEvaluating models...")
    results = evaluate_models_on_dataset(models, image_dir)
    
    if not results:
        print("Error: No results from evaluation")
        return
    
    # Find best model
    best_model, best_accuracy, summary = find_best_model(results)
    
    # Display results
    print("\n=== MODEL COMPARISON RESULTS ===")
    print(f"{'Model Name':<35} {'Accuracy':<12} {'Fracture Capable':<20} {'Predictions':<12}")
    print("-" * 80)
    
    fracture_models_count = 0
    for item in summary:
        model_name = item['model']
        accuracy = item['accuracy']
        fracture_capable = item['fracture_capable']
        predictions = item['total_predictions']
        
        if fracture_capable:
            fracture_models_count += 1
        
        accuracy_str = f"{accuracy:.4f}" if accuracy is not None else "N/A"
        fracture_str = "Yes" if fracture_capable else "No"
        
        # Mark best model
        marker = " ← BEST" if model_name == best_model and accuracy is not None else ""
        
        print(f"{model_name:<35} {accuracy_str:<12} {fracture_str:<20} {predictions:<12}{marker}")
    
    print("-" * 80)
    if best_model and best_accuracy is not None:
        print(f"\n🏆 WINNER: {best_model} with accuracy of {best_accuracy:.4f}")
    else:
        print(f"\n⚠️  Unable to determine winner (no ground truth labels provided)")
    
    print(f"\n📊 Summary:")
    print(f"  • Total models evaluated: {len(models)}")
    print(f"  • Fracture-capable models: {fracture_models_count}")
    print(f"  • Test images processed: {len(image_files)}")
    
    # Save results to file
    results_file = os.path.join(os.path.dirname(__file__), '..', 'results', 'model_comparison_results.json')
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    # Prepare results for saving
    save_results = {
        'summary': summary,
        'best_model': best_model,
        'best_accuracy': best_accuracy,
        'total_images': len(image_files),
        'detailed_results': results
    }
    
    try:
        with open(results_file, 'w') as f:
            json.dump(save_results, f, indent=2)
        print(f"\n💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Warning: Could not save results to file: {e}")

if __name__ == "__main__":
    main()