from pymongo import MongoClient

# 방법1 - URI
# mongodb_URI = "mongodb://localhost:27017/"
# client = MongoClient(mongodb_URI)

# 방법2 - HOST, PORT
client = MongoClient(host='localhost', port=27017)

print(client.list_database_names())

# DB 접근
# 방법1
# db = client.mydb

# 방법2
db = client['admin']