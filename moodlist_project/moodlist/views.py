from django.shortcuts import render
# !pip install facenet_pytorch

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from facenet_pytorch import MTCNN
from moodlist.cnn_model import MoodRecognitionModel
from rest_framework.views import APIView
from helpers import preprocess_image

# Define your class names for mood recognition
class_names = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise']

# Device configuration (assuming you have a GPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the model (assuming `new_model` is already defined and loaded)
new_model = MoodRecognitionModel(input_shape=1, hidden_units=128, dropout_rate=0.1)
checkpoint = torch.load('mood_v2.pth', map_location=torch.device('cpu'))
new_model.load_state_dict(checkpoint['model_state_dict'])
new_model.eval()
new_model.to(device)

def UploadPhotoAPIView(APIView):
    def post(self, request):
        # Get the uploaded image
        image = request.FILES['image']

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

            # Get the predicted mood
            predicted_mood = class_names[predicted_class]

            return render(request, 'result.html', {'predicted_mood': predicted_mood})
        else:
            return render(request, 'result.html', {'predicted_mood': 'No face detected in the image.'})

