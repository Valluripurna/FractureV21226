import numpy as np
from PIL import Image

# Create a black image
img_array = np.zeros((224, 224, 3), dtype=np.uint8)

# Add a white rectangle to simulate a bone
img_array[100:124, 50:174] = [255, 255, 255]

# Create an image from the array
img = Image.fromarray(img_array)

# Save the image
img.save("c:/Users/purna/OneDrive/Desktop/Fracture/test_images/test_image.png")
