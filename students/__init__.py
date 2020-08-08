from flask import Flask
import dotenv
import os
from pymongo import MongoClient
import redis

dotenv.load_dotenv()

app = Flask(__name__)

app.config['ENV'] = os.getenv('ENVIRONMENT')

URL_MONGO_CLIENT = f'mongodb://{os.getenv("DATABASE_HOST")}:{os.getenv("DATABASE_PORT")}/'
client_mongo = MongoClient(URL_MONGO_CLIENT)
db = client_mongo[os.getenv('DATABASE_NAME')]

collection_name = os.getenv('DATABASE_COLLECTION')
if collection_name not in db.list_collection_names():
  db.create_collection(collection_name)

collection = db.get_collection(collection_name)

r = redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'))

from students import routes