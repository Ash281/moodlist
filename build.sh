python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
npm install
npm run build
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput