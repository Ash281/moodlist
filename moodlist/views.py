from django.shortcuts import render
# !pip install facenet_pytorch

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from facenet_pytorch import MTCNN
from moodlist.cnn_model import MoodRecognitionModel
from rest_framework.views import APIView
from .helpers import preprocess_image
from rest_framework.response import Response
import os
from .models import Mood
from django.conf import settings
from django.shortcuts import redirect
import base64
import requests
import dotenv

env_path = os.path.join(settings.BASE_DIR, '.env')
dotenv.load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = 'http://127.0.0.1:8000/api/callback/'

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, 'mood_v4.pth')
# Define your class names for mood recognition
class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise']

# Device configuration (assuming you have a GPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

new_model = MoodRecognitionModel(input_shape=1, hidden_units=128, dropout_rate=0.25)
checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
new_model.load_state_dict(checkpoint['model_state_dict'])
new_model.eval()
new_model.to(device)
class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise']

class UploadPhotoAPIView(APIView):
    def post(self, request):
        Mood.objects.all().delete()
        # Get the uploaded image
        image = request.FILES['file']

        # Save the image to disk
        with open('uploaded_image.jpg', 'wb') as f:
            f.write(image.read())

        # Preprocess the image and perform inference
        face, input_tensor = preprocess_image('uploaded_image.jpg')

        if face is not None and input_tensor is not None:
            # Perform inference on the cropped face
            with torch.no_grad():
                output = new_model(input_tensor)

            # Assuming output is logits, apply softmax to get probabilities
            probabilities = F.softmax(output, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            for i, prob in enumerate(probabilities.squeeze().tolist()):
                print(f"{class_names[i]}: {prob:.4f}")
            print(predicted_class)

            # Get the predicted mood
            predicted_mood = class_names[predicted_class]
            Mood.objects.create(mood=predicted_mood)
            return Response({'predicted_mood': predicted_mood})  # Return JSON response
        else:
            return Response({'predicted_mood': 'No face detected in the image.'})
        
class GetMoodAPIView(APIView):
    def get(self, request):
        first_mood = Mood.objects.first()
        if first_mood:
            mood = first_mood.mood
            return Response({'mood': mood})
        else:
            return Response({'mood': 'No mood detected.'})
        
class ResetMoodAPIView(APIView):
    def post(self, request):
        Mood.objects.all().delete()
        return Response({'message': 'Mood reset successfully.'})

# redirect to Spotify login page for authentication and then redirect to the callback URL
def login(request):
    # Define the scopes for the Spotify API
    scope = 'user-read-private user-read-email user-library-read user-top-read'
    # Construct the URL for authentication on Spotify
    auth_url = f"https://accounts.spotify.com/authorize?client_id={SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}"
    # Redirect to the Spotify authentication URL
    return redirect(auth_url)

# callback URL to get the access token
class CallbackAPIView(APIView):
    # extract auth code from the URL after authentication
    def get(self, request):
        code = request.GET.get('code')
        
        response = requests.post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET
        }).json()

        access_token = response.get('access_token')
        token_type = response.get('token_type')
        refresh_token = response.get('refresh_token')
        expires_in = response.get('expires_in')
        error = response.get('error')

        if error:
            return Response({'error': error})
        else:
            

# check if the access token is available in the cookies
class GetTokenAPIView(APIView):
    def get(self, request):
        print(request.COOKIES)
        access_token = request.COOKIES.get('access_token')
        return Response({'access_token': access_token})