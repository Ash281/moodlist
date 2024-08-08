from django.shortcuts import render
# !pip install facenet_pytorch

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from facenet_pytorch import MTCNN
from moodlist.cnn_model import MoodRecognitionModel
from rest_framework.views import APIView
from .helpers import preprocess_image, get_user_tokens, update_or_create_user_tokens, is_spotify_authenticated
from rest_framework.response import Response
import os
from .models import Mood, SpotifyToken
from django.conf import settings
from django.shortcuts import redirect
import base64
import requests
import dotenv

env_path = os.path.join(settings.BASE_DIR, '.env')
dotenv.load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
# REDIRECT_URI = 'http://127.0.0.1:8000/api/callback/'
REDIRECT_URI = 'https://moodlist-production.up.railway.app/api/callback/'

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
    print("Login")
    print(SPOTIFY_CLIENT_ID)
    print(REDIRECT_URI)
    print(SPOTIFY_CLIENT_SECRET)
    # Define the scopes for the Spotify API
    scope = 'user-read-private user-read-email user-library-read user-top-read playlist-modify-public playlist-modify-private'
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

        if not request.session.exists(request.session.session_key):
            request.session.create()

        session_id = request.session.session_key
        update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token)

        return redirect('https://moodlist-production.up.railway.app/')
        # return redirect('http://127.0.0.1:8000/')
            
# check if the access token is available in the cookies
class IsAuthenticatedAPIView(APIView):
    def get(self, request):
        print(self.request.session.session_key)
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'is_authenticated': is_authenticated, 'session_key': self.request.session.session_key})
    
class GetTopTracksAPIView(APIView):
    def get(self, request):
        mood = request.query_params.get('mood')
        print("Mood:", mood)

        if is_spotify_authenticated(request.session.session_key):
            print("Authenticated")
            user_tokens = get_user_tokens(request.session.session_key)
            access_token = user_tokens.access_token

            # Fetch liked songs from Spotify
            response = requests.get('https://api.spotify.com/v1/me/tracks', headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            },
            params={'limit': 50}
            )

            print("Status Code:", response.status_code)
            print("Response Text:", response.text)  # Log the raw response text

            if response.status_code == 200:
                try:
                    tracks = response.json()['items']
                    print(len(tracks), "tracks found")
                    filtered_tracks = filter_songs_by_mood(mood, request, tracks)
                    
                    # Limit to 50 tracks
                    track_ids = [track['uri'] for track in filtered_tracks][:50]
                    
                    playlist_id = create_playlist(track_ids, access_token, mood)
                    print("Playlist ID:", playlist_id)
                    
                    for uri in track_ids:
                        print(uri)
                    
                    return Response({'playlist_id': playlist_id})
                except ValueError as e:
                    print("Error parsing JSON:", e)
                    return Response({'error': 'Failed to parse response from Spotify'}, status=500)
            else:
                return Response({'error': 'Failed to fetch liked songs from Spotify', 'details': response.text}, status=response.status_code)

        return Response({'error': 'User not authenticated'}, status=401)


    
def filter_songs_by_mood(mood, request, tracks):
    filtered_tracks = []
    for item in tracks:
        track = item['track']  # Extract the track info
        track_id = track['id']
        print(mood)
        if is_spotify_authenticated(request.session.session_key):
            print("Authenticated")
            user_tokens = get_user_tokens(request.session.session_key)
            access_token = user_tokens.access_token
            track_features = get_track_features(track_id, access_token)
            if track_features:
                if mood == 'happy' and track_features['valence'] > 0.6:
                    filtered_tracks.append(track)
                elif mood == 'sad' and track_features['valence'] < 0.4:
                    filtered_tracks.append(track)
                elif mood == 'angry' and track_features['energy'] < 0.4 and track_features['valence'] < 0.6:
                    filtered_tracks.append(track)
                elif mood == 'surprise' and track_features['valence'] > 0.4 and track_features['energy'] > 0.6:
                    filtered_tracks.append(track)
                elif mood == 'fear' and track_features['valence'] > 0.5 and track_features['energy'] < 0.5:
                    filtered_tracks.append(track)
                elif mood == 'disgust' and track_features['valence'] < 0.5 and track_features['energy'] > 0.5:
                    filtered_tracks.append(track)
    return filtered_tracks

    
def get_track_features(track_id, access_token):
    response = requests.get(f'https://api.spotify.com/v1/audio-features/{track_id}', headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    })
    if response.status_code == 200:
        return response.json()
    return None

def create_playlist(track_ids, access_token, mood):
    # Remove duplicates and limit to 50
    track_ids = list(set(track_ids))[:50]
    
    response = requests.post('https://api.spotify.com/v1/me/playlists', headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }, json={
        'name': f'Moodlist: {mood}',
        'description': 'Playlist generated by Moodlist',
        'public': True
    })
    
    if response.status_code == 201:
        playlist_id = response.json()['id']
        add_tracks_to_playlist(playlist_id, track_ids, access_token)
        return playlist_id
    return None

def add_tracks_to_playlist(playlist_id, track_ids, access_token):
    track_ids = list(set(track_ids))[:50]  # Ensure only unique tracks and limit to 50

    while track_ids:
        batch = track_ids[:100]  # Spotify API allows up to 100 tracks per request
        track_ids = track_ids[100:]
        response = requests.post(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks', headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }, json={
            'uris': batch
        })
        if response.status_code != 201:
            return False
    return True


