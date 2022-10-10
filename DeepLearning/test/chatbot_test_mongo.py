# from config.DatabaseConfig import *
# from utils.Database import Database
# from utils.Preprocess import Preprocess
from pymongo import MongoClient
import pprint

# 몽고 디비 연결
client = MongoClient(host='localhost', port=27017)

# print(client.list_database_names())

# 방법2
db = client['admin'] # admin db 연결
# collection = db['time'] # time collection 확인
# print(collection)

# collection list 확인
print(db.list_collection_names()) # ['time', 'test', 'system.version']

time = db.time # 변수에 collection 저장
pprint.pprint(time.find_one({"room": "차235"})) # 원하는 객체 찾음
pprint.pprint(time.find_one({"room": "차320"})) # 원하는 객체 찾음



# 전처리 객체 생성
p = Preprocess(word2index_dic='../train_tools/dict/chatbot_dict.bin',
               userdic='../utils/user_dic.tsv')

# # 질문/답변 학습 디비 연결 객체 생성
# db = Database(
#     host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME
# )
# db.connect()    # 디비 연결

# 원문
# query = "오전에 탕수육 10개 주문합니다"
# query = "화자의 질문 의도를 파악합니다."
# query = "안녕하세요"
query = "자장면 주문할게요"
query = "내일 오전 차미리사관 빈 강의실 어디야?"
query = "차관 오늘 이용할 수 있어?"
query = '지금 차320 사용 가능해?'
query = '오늘 차관 비었어?'
query = "내일 오전 차미리사관 빈 강의실 어디야?"

# 의도 파악
from models.intent.IntentModel import IntentModel
intent = IntentModel(model_name='../models/intent/intent_model.h5', proprocess=p)
predict = intent.predict_class(query)
intent_name = intent.labels[predict]

# 개체명 인식
from models.ner.NerModel import NerModel
ner = NerModel(model_name='../models/ner/ner_model.h5', proprocess=p)
predicts = ner.predict(query)
ner_tags = ner.predict_tags(query)

print("질문 : ", query)
print("=" * 100)
print("의도 파악 : ", intent_name)
print("개체명 인식 : ", predicts)
print("답변 검색에 필요한 NER 태그 : ", ner_tags)
print("=" * 100)

# # 답변 검색
# from utils.FindAnswer import FindAnswer
#
# try:
#     f = FindAnswer(db)
#     answer_text, answer_image = f.search(intent_name, ner_tags)
#     answer = f.tag_to_word(predicts, answer_text)
# except:
#     answer = "죄송해요 무슨 말인지 모르겠어요"
#
# print("답변 : ", answer)
#
# db.close() # 디비 연결 끊음