from pymongo import MongoClient
import certifi
from config import MONGO_URL
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
df = pd.read_csv(BASE_DIR / 'DataBase/answer_data.csv')
# df.drop('Unnamed: 0', axis=1, inplace=True)

print(df.info())

client = MongoClient(MONGO_URL)
db = client['DS']

for i in range(len(df)):
    answer_data = {
        "intent": df.iloc[i]["Intent"],
        "ner": df.iloc[i]["NER"],
        "answer": df.iloc[i]["Answer"],
    }
    print(answer_data)
    dpInsert = db.answer.insert_one(answer_data)  # db에 정보 입력

print("finish!")
