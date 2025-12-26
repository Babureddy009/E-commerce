import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads/products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

MYSQL_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}


