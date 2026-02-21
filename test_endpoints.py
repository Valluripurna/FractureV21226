import requests
import json

# Test health endpoint
try:
    response = requests.get('http://localhost:5000/health')
    print("Health endpoint:", response.status_code, response.json())
except Exception as e:
    print("Health endpoint error:", e)

print("---")

# Test chat endpoint
try:
    response = requests.post('http://localhost:5000/chat', 
                           json={'message': 'What should I do for fracture recovery?'})
    print("Chat endpoint:", response.status_code, response.json())
except Exception as e:
    print("Chat endpoint error:", e)

print("---")

# Test model status endpoint
try:
    response = requests.get('http://localhost:5000/model_status')
    print("Model status endpoint:", response.status_code, response.json())
except Exception as e:
    print("Model status endpoint error:", e)