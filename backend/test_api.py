import requests
import json

# Test ensemble prediction
print('Testing Ensemble Prediction API...')
print('=' * 70)

with open('../test_images/test_image.png', 'rb') as f:
    files = {'file': f}
    resp = requests.post('http://localhost:5000/predict', files=files, timeout=30)

if resp.status_code == 200:
    print('✅ Prediction successful!')
    data = resp.json()
    
    print('\nPREDICTION RESULT:')
    print('-' * 70)
    print(f"Fracture Detected: {data['fracture_detected']}")
    print(f"Probability: {data['probability']:.4f}")
    print(f"Confidence: {data['confidence']*100:.1f}%")
    
    print('\nMODEL INFORMATION:')
    print('-' * 70)
    print(f"Model Version: {data['model_version']}")
    print(f"Model Accuracy: {data['model_accuracy']}")
    print(f"Body Region: {data['body_region']}")
    
    if 'annotated_image' in data:
        print('\n✅ Annotated image generated')
    
    print('\n' + '=' * 70)
    print('FULL RESPONSE:')
    print('-' * 70)
    # Don't print the full base64 image, just show keys
    display_data = dict(data)
    if 'annotated_image' in display_data:
        display_data['annotated_image'] = '<base64_encoded_image>'
    print(json.dumps(display_data, indent=2))
    
else:
    print(f'❌ Error: {resp.status_code}')
    print(resp.text)
