python -m venv venv
venv\Scripts\activate
python3 -m pip install -r requirements.txt
npm install
npm run build
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput