#!/usr/bin/env python3
"""
Test script to check model name matching logic.
"""

def test_matching(model_name):
    """Test the model matching logic."""
    print(f"Testing model name: '{model_name}'")
    
    if 'efficientnet' in model_name.lower():
        print("  -> Matches efficientnet branch")
    elif 'fracnet' in model_name.lower():
        print("  -> Matches fracnet branch")
    elif 'mura' in model_name.lower():
        print("  -> Matches mura branch")
    elif 'resnet50' in model_name.lower():
        print("  -> Matches resnet50 branch")
    elif 'densenet' in model_name.lower() and 'fracture' in model_name.lower():
        print("  -> Matches densenet fracture branch")
    elif model_name in ['txv_all', 'fracture_model']:
        print("  -> Matches txv_all branch")
    elif model_name == 'rsna_model':
        print("  -> Matches rsna_model branch")
    elif model_name == 'vindr_model':
        print("  -> Matches vindr_model branch")
    else:
        print("  -> Goes to default branch")

def main():
    """Test various model names."""
    model_names = [
        'resnet50_fracture_model',
        'densenet121_fracture_model',
        'efficientnet_fracture_model',
        'fracnet_model',
        'mura_model_pytorch',
        'rsna_model',
        'vindr_model',
        'fracture_model'
    ]
    
    for name in model_names:
        test_matching(name)
        print()

if __name__ == "__main__":
    main()