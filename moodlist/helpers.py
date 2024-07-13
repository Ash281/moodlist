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
from .models import SpotifyToken
from datetime import datetime, timedelta
from django.utils import timezone
from requests import post, get

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = 'http://127.0.0.1:8000/api/callback/'

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, 'mood_v4.pth')
# Define your class names for mood recognition
class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise']

# Device configuration (assuming you have a GPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the model (assuming `new_model` is already defined and loaded)
new_model = MoodRecognitionModel(input_shape=1, hidden_units=128, dropout_rate=0.25)
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

def get_user_tokens(session_id):
    print(session_id)
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    print(user_tokens)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None
    
def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    # when the token expires as a timestamp
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    if tokens:
        tokens.access_token = access_token
        tokens.token_type = token_type
        tokens.expires_in = expires_in
        tokens.refresh_token = refresh_token
        tokens.save(update_fields=['access_token', 'token_type', 'expires_in', 'refresh_token'])
    else:
        tokens = SpotifyToken(user=session_id, access_token=access_token, token_type=token_type, expires_in=expires_in, refresh_token=refresh_token)
        tokens.save()
    print("Token updated or created: ", tokens)

def is_spotify_authenticated(session_id):
    user_tokens = get_user_tokens(session_id)
    if user_tokens:
        expiry = user_tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)
        return True
    return False

def refresh_spotify_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }).json()
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token)