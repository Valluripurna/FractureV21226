#!/usr/bin/env python3
"""
Cleanup script to remove unused model files that fail to load due to missing dependencies.
"""

import os
import sys

def cleanup_unused_models():
    """Remove model files that cannot be loaded due to missing dependencies."""
    
    # Define the models directory
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    
    # Models that fail to load due to missing torchxrayvision
    unused_models = [
        'rsna_model.pth',
        'vindr_model.pth', 
        'fracture_model.pth'
    ]
    
    print("=== MODEL CLEANUP SCRIPT ===")
    print(f"Checking models directory: {models_dir}")
    
    # Check if models directory exists
    if not os.path.exists(models_dir):
        print("❌ Models directory not found!")
        return
    
    # List all model files
    all_models = os.listdir(models_dir)
    print(f"\nTotal models found: {len(all_models)}")
    for model in all_models:
        print(f"  - {model}")
    
    # Identify unused models to remove
    models_to_remove = []
    for model in unused_models:
        model_path = os.path.join(models_dir, model)
        if os.path.exists(model_path):
            models_to_remove.append((model, model_path))
    
    if not models_to_remove:
        print("\n✅ No unused models found to remove")
        return
    
    print(f"\nFound {len(models_to_remove)} unused models to remove:")
    for model, path in models_to_remove:
        size_mb = os.path.getsize(path) / (1024 * 1024)
        print(f"  - {model} ({size_mb:.1f} MB)")
    
    # Confirm removal
    print("\nRemoving unused models...")
    removed_count = 0
    
    for model, path in models_to_remove:
        try:
            os.remove(path)
            print(f"  ✅ Removed: {model}")
            removed_count += 1
        except Exception as e:
            print(f"  ❌ Failed to remove {model}: {e}")
    
    print(f"\n=== CLEANUP COMPLETE ===")
    print(f"Removed {removed_count} unused model files")
    print("Freed disk space by removing models that failed to load due to missing torchxrayvision dependency")

if __name__ == "__main__":
    cleanup_unused_models()