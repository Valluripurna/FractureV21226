import requests
import json

# Test if backend is responding
try:
    response = requests.get('http://localhost:5000/health')
    print("Backend health check:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Backend health check failed:", e)

# Test if frontend is accessible
try:
    response = requests.get('http://localhost:3000')
    print("\nFrontend accessibility:", response.status_code)
except Exception as e:
    print("Frontend accessibility check failed:", e)