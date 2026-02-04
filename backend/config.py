import os
from dotenv import load_dotenv
import logging

log = logging.getLogger(__name__)



class Config:
    
    def __init__(self, testing=True):
        load_dotenv()
        
        if testing:
            self.SQLALCHEMY_DATABASE_URI = os.environ["TEST_DATABASE_URL"]
            self.SECRET_KEY = os.getenv("TEST_SECRET_KEY", "dev")
            logging.info("Using test database configuration.")
        else:
            self.SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]  
            self.SECRET_KEY = os.getenv("SECRET_KEY", "dev")
            logging.info("Using production database configuration.")
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False