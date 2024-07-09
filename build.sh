python -m venv venv
venv\Scripts\activate
python3 -m pip install -r requirements.txt
npm install
npm run build
pip install django
pip install djangorestframework
pip install django-cors-headers
pip install whitenoise
pip install torch
pip install gunicorn
pip install torchvision
pip install facenet-pytorch
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput