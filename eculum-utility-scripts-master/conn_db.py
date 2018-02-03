import pymongo
import os

client = pymongo.MongoClient(os.environ['DB_STRING'])
db = client.get_database("eculum")
