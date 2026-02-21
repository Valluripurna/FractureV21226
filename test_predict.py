import requests
import json

# First, let's login to get a token
login_data = {
    "email": "test@example.com",
    "password": "testpassword"
}

# For testing purposes, let's just use a dummy token since we're focusing on the predict endpoint
# In a real scenario, you would get this from the login endpoint

# Read a test image
try:
    with open("test_images/test_image.png", "rb") as f:
        image_data = f.read()
    
    # Send the image to the predict endpoint
    files = {"file": ("test_image.png", image_data, "image/png")}
    headers = {
        "Authorization": "Bearer dummy_token_for_testing"
    }
    
    print("Sending request to predict endpoint...")
    response = requests.post(
        "http://localhost:5000/predict",
        files=files,
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except FileNotFoundError:
    print("Test image not found. Please make sure test_images/test_image.png exists.")
except Exception as e:
    print(f"Error: {e}")