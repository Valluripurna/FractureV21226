import requests
response = requests.get('https://huggingface.co/api/models?search=fracture')
models = response.json()
for m in models[:15]:
    print(f'https://huggingface.co/{m[\"id\"]}')
