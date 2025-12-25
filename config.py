import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

SECRET_KEY = "supersecretkey"



MYSQL_CONFIG = {
    "host": "host.docker.internal",
    "user": "root",
    "password": "Babu@123",
    "database": "ecommerce"
}

SECRET_KEY = "supersecretkey"

