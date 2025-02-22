import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://flaskuser:flaskpassword@localhost:5432/flaskdb")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
