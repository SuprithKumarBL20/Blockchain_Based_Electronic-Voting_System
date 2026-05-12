import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'db.sqlite3').replace('\\', '/')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Face Recognition
    FACE_MODEL_PATH = 'ai/model.onnx'
    FACE_THRESHOLD = 0.6
    
    # OTP Configuration
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 5
    
    # Blockchain Configuration
    BLOCKCHAIN_DIFFICULTY = 4
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'static/images'
    
    # Election Configuration
    ELECTION_START_TIME = None
    ELECTION_END_TIME = None
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    
    # Development
    DEBUG = True
    TESTING = False