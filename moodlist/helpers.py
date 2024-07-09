from django.shortcuts import render
# !pip install facenet_pytorch

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from facenet_pytorch import MTCNN
from moodlist.cnn_model import MoodRecognitionModel
from rest_framework.views import APIView
import os

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, 'mood_v4.pth')
# Define your class names for mood recognition
class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise']

# Device configuration (assuming you have a GPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the model (assuming `new_model` is already defined and loaded)
new_model = MoodRecognitionModel(input_shape=1, hidden_units=128, dropout_rate=0.1)
checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
new_model.load_state_dict(checkpoint['model_state_dict'])
new_model.eval()
new_model.to(device)

# Function to preprocess image and detect/crop face
def preprocess_image(image_path):
    # Load image
    image = Image.open(image_path).convert('RGB')

    # Initialize MTCNN for face detection
    mtcnn = MTCNN(keep_all=True, device=device)

    # Detect faces
    boxes, probs = mtcnn.detect(image)

    # Ensure a face was detected
    if boxes is not None:
        # Select the first face (you may modify this logic based on your requirements)
        box = boxes[0]
        
        # Convert box coordinates to integers
        box = [int(b) for b in box]

        # Crop face from image
        face = image.crop((box[0], box[1], box[2], box[3]))

        # Preprocess cropped face for model input
        transform = transforms.Compose([
            transforms.Resize((48, 48)),
            transforms.Grayscale(num_output_channels=1),
            transforms.ToTensor(),
        ])
        face_tensor = transform(face).unsqueeze(0).to(device)

        return face, face_tensor

    else:
        print("No face detected in the image.")
        return None, None
""" 
# Example usage
image_path = 'uncropped_6.jpg'
face, input_tensor = preprocess_image(image_path)
image = Image.open(image_path).convert('RGB')

if face is not None and input_tensor is not None:
    # Perform inference on the cropped face
    with torch.no_grad():
        output = new_model(input_tensor)

    # Assuming output is logits, apply softmax to get probabilities
    probabilities = F.softmax(output, dim=1)
    predicted_class = torch.argmax(probabilities, dim=1).item()
 """