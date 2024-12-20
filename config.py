# config.py
import os

# Base directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'  # Needed for flashing messages
