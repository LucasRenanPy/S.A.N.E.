import os
from dotenv import load_dotenv


load_dotenv()



class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")

    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")

    SESSION_TYPE = "filesystem"
    
    UPLOAD_FOLDER = "static/uploads"

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}