import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aifitness-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///fitness.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Calories per rep estimates (MET-based approximation)
    CALORIES_PER_REP = {
        'squat': 0.32,
        'pushup': 0.29,
        'bicep_curl': 0.18,
    }
