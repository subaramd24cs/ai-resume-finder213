from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/")
        client = MongoClient(mongo_uri)
        return client.resume_finder_db
    except Exception as e:
        print("Could not connect to MongoDB:", e)
        return None
