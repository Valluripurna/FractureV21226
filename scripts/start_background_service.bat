@echo off
echo Starting Background Model Evaluator Service...
echo This will run in the background and automatically determine the best model for fracture detection.
echo Press Ctrl+C to stop the service.

cd /d "c:\Users\purna\Desktop\Fracture\scripts"
python background_evaluator.py

pause