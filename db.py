import json

from pymongo import MongoClient
import certifi

client = MongoClient("mongodb+srv://test:0925@cluster.erzgpyh.mongodb.net/?retryWrites=true&w=majority",
                     tlsCAFile=certifi.where())

chat_db = client.get_database("DS")
lib_collection = chat_db.get_collection("library")
file_name='notice.json'

with open(file_name, 'r', encoding='utf-8-sig') as f:
    file_data = json.load(f)
    result = lib_collection.insert_one(file_data)
