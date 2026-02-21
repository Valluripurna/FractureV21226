# 🏥 Bone Fracture Detection System

A comprehensive system for detecting bone fractures in X-ray images using multiple deep learning models.

## 📁 Folder Structure

```
Fracture/
├── backend/              # Flask API backend
├── docs/                 # Documentation files
├── frontend/             # React frontend application
├── models/               # Pre-trained model files (.pth)
├── scripts/              # Utility scripts for model saving and analysis
├── tests/                # Test scripts for model validation
└── torchxrayvision/      # Medical imaging library
```

## 🧠 Models

All models are stored in the `models/` directory:
- EfficientNet-B4 Fracture Detection Model
- FracNet Model
- MURA Model (PyTorch Version)

>Note: TorchXRayVision models (ALL, RSNA, and VinDR) have been removed due to missing dependencies. To use these models, please install the torchxrayvision library.

## 🚀 Quick Start

1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Start the backend server:
   ```bash
   python app.py
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

4. Start the frontend:
   ```bash
   npm start
   ```

## 📖 Documentation

See `docs/MODEL_INVENTORY.md` for detailed information about all models including:
- Accuracy claims
- Dataset information
- Performance on unseen X-rays
- Recommendations for use

## 🧪 Testing

Run model tests with:
```bash
cd tests
python test_models.py
```

## 🤖 Automatic Model Selection

The system automatically determines which model achieves the highest accuracy on unseen X-ray images through a background evaluation process:

1. **Continuous Background Evaluation**: The system periodically evaluates all models using test images
2. **Automatic Model Selection**: The best performing model is automatically selected for inference
3. **Transparent Operation**: This process runs completely in the background without user intervention

To enable automatic model selection:
1. Place test X-ray images in the `test_images` directory
2. The background evaluator will automatically assess model performance
3. The system will use the best model for all subsequent predictions

Start the background evaluator:
```bash
cd scripts
python background_evaluator.py
```

## 🛠️ Scripts

Utility scripts in the `scripts/` directory:
- Model saving scripts
- Analysis tools
- Model evaluation utilities
- `compare_model_accuracy.py` - Manual model comparison
- `background_evaluator.py` - Automatic background evaluation
- `test_model_loading.py` - Verify model loading capabilities

## 📦 Requirements

- Python 3.7+
- PyTorch 1.7+
- Flask
- React
- Node.js