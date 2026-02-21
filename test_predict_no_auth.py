import requests
import json

# Read a test image
try:
    with open("test_images/test_image.png", "rb") as f:
        image_data = f.read()
    
    # Send the image to the predict endpoint WITHOUT authentication
    # This will help us determine if the issue is with JWT or something else
    files = {"file": ("test_image.png", image_data, "image/png")}
    
    print("Sending request to predict endpoint (no auth)...")
    response = requests.post(
        "http://localhost:5000/predict",
        files=files
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except FileNotFoundError:
    print("Test image not found. Please make sure test_images/test_image.png exists.")
except Exception as e:
    print(f"Error: {e}")