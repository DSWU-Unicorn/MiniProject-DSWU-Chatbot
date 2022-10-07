from pymongo import MongoClient
import certifi
from config import MONGO_URL
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / 'DataBase/timetable.csv')

df.drop('Unnamed: 0', axis=1, inplace=True)
df = df.dropna()

print(df.info())

client = MongoClient(MONGO_URL)
db = client['DS']

for i in range(len(df)):
    timetable_info = {
        "교시": df.iloc[i]["timetable"],
        "시간": df.iloc[i]["lec_time"],
    }
    print(timetable_info)
    dpInsert = db.inform.insert_one(timetable_info)  # db에 정보 입력

print("timetable_info insert finish!")
