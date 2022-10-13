from pymongo import MongoClient
import certifi
from config import MONGO_URL
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / 'DataBase/defined_data_0930.csv')
df.drop('Unnamed: 0', axis=1, inplace=True)
df = df.dropna()

print(df.info())

client = MongoClient(MONGO_URL)
db = client['DS']

for i in range(len(df)):
    class_info = {
        "강의실" : df.iloc[i]["room"],
        "강의시간" : df.iloc[i]["time"],
        # 강의시간 to 시간 필요하지 않나?

    }
    print(class_info)
    dpInsert = db.inform.insert_one(class_info)  # db에 정보 입력

print("finish!")