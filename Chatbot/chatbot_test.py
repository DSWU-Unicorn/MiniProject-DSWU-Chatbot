from config.DatabaseConfig import *
from utils.Database import Database
from utils.Preprocess import Preprocess
from pymongo import MongoClient


# 몽고 디비 연결
client = MongoClient(host='localhost', port=27017)

db = client['admin'] # admin db 연결

info = db.info # 변수에 collection 저장
test = db.test

# 전처리 객체 생성
p = Preprocess(word2index_dic='../train_tools/dict/chatbot_dict.bin',
               userdic='../utils/user_dic.tsv')

# 원문
# query = "오전에 탕수육 10개 주문합니다"
# query = "화자의 질문 의도를 파악합니다."
# query = "안녕하세요"
query = "자장면 주문할게요"
query = "내일 오전 차미리사관 빈 강의실 어디야?"
query = '지금 차320 사용 가능해?'
query = "안녕하세요 반갑습니다." # 인사
query = "안녕하세요 좋은 날입니다." # 기타 - 답변 오류
query = "오늘 오전 차미리사관 빈 강의실 어디야?" # 강의실, B_ROOM, B_DT
query = "차관 오늘 이용할 수 있어?" # 강의실, dt, dt
query = '차관 비었어?' # 강의실
query = "내일 오전 차미리사관 빈 강의실 어디야?" # 강의실, B_ROOM, B_DT

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

# print("예측 값에서 입력된 단어 찾기 ")
# for word, tag in predicts:
#     print(word, tag) # word - 입력된 값, tag - 인식된 tag

# 답변 검색
from utils.FindAnswer import FindAnswer
time = []
place = []
today = ["오늘", "지금", "현재"]

test = db.test # 변수에 collection 저장
if intent_name == "기타":
    answer_text = test.find_one({"Intent": "기타"})['Answer']

elif intent_name == "인사":
    answer_text = test.find_one({"Intent": "인사"})['Answer']

# elif intent_name == "욕설":
#     answer_text = test.find_one({"Intent": "욕설"})['Answer']


# 날짜, 강의실 정보가 모두 입력되었을 때
elif intent_name == "강의실" and "B_ROOM" in ner_tags and "B_DT" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_ROOM, B_DT"})['Answer']
    # 인식된 태그를 입력한 단어로 변환
    # 답변을 출력할 수 있도록 변수와 리스트에 저장
    for word, tag in predicts:
        if tag == "B_ROOM":
            place.append(word)
        if tag == "B_DT":
            time.append(word)
    # print(place, time) # 입력된 장소 정보와 시간 정보
    # 오늘 이라는 값을 리스트에 넣어 확인하려 했는데 그럼 for 하나 더 써야 해서 그냥 이렇게 함
    if '오늘' or '지금' or '현재' in time: # 오늘 강의실 정보를 요청하는 거라면
        # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
        # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
        place = "차235"
        # room, time 을 다영이 정보로 변환하기
        if db.info.find_one({'room': place}):
            class_time = db.info.find_one({'room': place})['time']
            new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
            # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
            class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
        print(class_list)
    else:
        pass
        # time에 저장된 날짜로 검색하면 된다

# 강의실 정보만 입력되었을 때, 날짜 정보는 입력 안됨
# 오늘을 기준으로 돌리면 된다
elif intent_name == "강의실" and "B_ROOM" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_ROOM"})['Answer']
    for word, tag in predicts:
        if tag == "B_ROOM":
            place = word
        # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
        # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
    place = "차235"
    # room, time 을 다영이 정보로 변환하기
    if db.info.find_one({'room': place}):
        class_time = db.info.find_one({'room': place})['time']
        new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
        # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
        class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
    print(class_list)


# 날짜 정보만 입력되고 강의실 정보는 입력되지 않았을 때
# 강의실 정보를 한번 더 물어보기
elif intent_name == "강의실" and "B_DT" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_DT"})['Answer']

    # answer_text = test.find_one({"Intent": "강의실"}, {"NER": "B_ROOM"})['Answer']
    # print(answer_text)

elif intent_name == "강의실" and "B_DT" not in ner_tags and "B_ROOM" not in ner_tags:
    answer_text = test.find_one({"Intent": "강의실"})['Answer']

try:
    pass
    # if intent_name == "강의실" and "B_ROOM" in ner_tags:
    #     answer_text = test.find_one({"의도(Intent)":"강의실"})['답변(Answer)']
    #     print(answer_text)

except:
    answer_text = "죄송합니다. 이해하지 못했어요 다시 한번 말씀해주세요"
#
print("답변 : ", answer_text)
# print("답변 : ", answer)
#
# db.close() # 디비 연결 끊음

from config.DatabaseConfig import *
from utils.Database import Database
from utils.Preprocess import Preprocess
from pymongo import MongoClient


# 몽고 디비 연결
client = MongoClient(host='localhost', port=27017)

db = client['admin'] # admin db 연결

info = db.info # 변수에 collection 저장
test = db.test

# 전처리 객체 생성
p = Preprocess(word2index_dic='../train_tools/dict/chatbot_dict.bin',
               userdic='../utils/user_dic.tsv')

# 원문
# query = "오전에 탕수육 10개 주문합니다"
# query = "화자의 질문 의도를 파악합니다."
# query = "안녕하세요"
query = "자장면 주문할게요"
query = "내일 오전 차미리사관 빈 강의실 어디야?"
query = '지금 차320 사용 가능해?'
query = "안녕하세요 반갑습니다." # 인사
query = "안녕하세요 좋은 날입니다." # 기타 - 답변 오류
query = "오늘 오전 차미리사관 빈 강의실 어디야?" # 강의실, B_ROOM, B_DT
query = "차관 오늘 이용할 수 있어?" # 강의실, dt, dt
query = '차관 비었어?' # 강의실
query = "내일 오전 차미리사관 빈 강의실 어디야?" # 강의실, B_ROOM, B_DT

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

# print("예측 값에서 입력된 단어 찾기 ")
# for word, tag in predicts:
#     print(word, tag) # word - 입력된 값, tag - 인식된 tag

# 답변 검색
from utils.FindAnswer import FindAnswer
time = []
place = []
today = ["오늘", "지금", "현재"]

test = db.test # 변수에 collection 저장
if intent_name == "기타":
    answer_text = test.find_one({"Intent": "기타"})['Answer']

elif intent_name == "인사":
    answer_text = test.find_one({"Intent": "인사"})['Answer']

elif intent_name == "욕설":
    answer_text = test.find_one({"Intent": "욕설"})['Answer']


# 날짜, 강의실 정보가 모두 입력되었을 때
elif intent_name == "강의실" and "B_ROOM" in ner_tags and "B_DT" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_ROOM, B_DT"})['Answer']
    # 인식된 태그를 입력한 단어로 변환
    # 답변을 출력할 수 있도록 변수와 리스트에 저장
    for word, tag in predicts:
        if tag == "B_ROOM":
            place.append(word)
        if tag == "B_DT":
            time.append(word)
    # print(place, time) # 입력된 장소 정보와 시간 정보
    # 오늘 이라는 값을 리스트에 넣어 확인하려 했는데 그럼 for 하나 더 써야 해서 그냥 이렇게 함
    if '오늘' or '지금' or '현재' in time: # 오늘 강의실 정보를 요청하는 거라면
        # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
        # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
        place = "차235"
        # room, time 을 다영이 정보로 변환하기
        if db.info.find_one({'room': place}):
            class_time = db.info.find_one({'room': place})['time']
            new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
            # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
            class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
        print(class_list)
    else:
        pass
        # time에 저장된 날짜로 검색하면 된다

# 강의실 정보만 입력되었을 때, 날짜 정보는 입력 안됨
# 오늘을 기준으로 돌리면 된다
elif intent_name == "강의실" and "B_ROOM" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_ROOM"})['Answer']
    for word, tag in predicts:
        if tag == "B_ROOM":
            place = word
        # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
        # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
    place = "차235"
    # room, time 을 다영이 정보로 변환하기
    if db.info.find_one({'room': place}):
        class_time = db.info.find_one({'room': place})['time']
        new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
        # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
        class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
    print(class_list)


# 날짜 정보만 입력되고 강의실 정보는 입력되지 않았을 때
# 강의실 정보를 한번 더 물어보기
elif intent_name == "강의실" and "B_DT" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_DT"})['Answer']

    # answer_text = test.find_one({"Intent": "강의실"}, {"NER": "B_ROOM"})['Answer']
    # print(answer_text)

elif intent_name == "강의실" and "B_DT" not in ner_tags and "B_ROOM" not in ner_tags:
    answer_text = test.find_one({"Intent": "강의실"})['Answer']

try:
    pass
    # if intent_name == "강의실" and "B_ROOM" in ner_tags:
    #     answer_text = test.find_one({"의도(Intent)":"강의실"})['답변(Answer)']
    #     print(answer_text)

except:
    answer_text = "죄송합니다. 이해하지 못했어요 다시 한번 말씀해주세요"
#
print("답변 : ", answer_text)
# print("답변 : ", answer)
#
# db.close() # 디비 연결 끊음

from config.DatabaseConfig import *
from utils.Database import Database
from utils.Preprocess import Preprocess
from pymongo import MongoClient


# 몽고 디비 연결
client = MongoClient(host='localhost', port=27017)

db = client['admin'] # admin db 연결

info = db.info # 변수에 collection 저장
test = db.test

# 전처리 객체 생성
p = Preprocess(word2index_dic='../train_tools/dict/chatbot_dict.bin',
               userdic='../utils/user_dic.tsv')

# 원문
# query = "오전에 탕수육 10개 주문합니다"
# query = "화자의 질문 의도를 파악합니다."
# query = "안녕하세요"
query = "자장면 주문할게요"
query = "내일 오전 차미리사관 빈 강의실 어디야?"
query = '지금 차320 사용 가능해?'
query = "안녕하세요 반갑습니다." # 인사
query = "안녕하세요 좋은 날입니다." # 기타 - 답변 오류
query = "오늘 오전 차미리사관 빈 강의실 어디야?" # 강의실, B_ROOM, B_DT
query = "차관 오늘 이용할 수 있어?" # 강의실, dt, dt
query = '차관 비었어?' # 강의실
query = "내일 오전 차미리사관 빈 강의실 어디야?" # 강의실, B_ROOM, B_DT

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

# print("예측 값에서 입력된 단어 찾기 ")
# for word, tag in predicts:
#     print(word, tag) # word - 입력된 값, tag - 인식된 tag

# 답변 검색
time = []
place = []
today = ["오늘", "지금", "현재"]

test = db.test # 변수에 collection 저장
if intent_name == "기타":
    answer_text = test.find_one({"Intent": "기타"})['Answer']

elif intent_name == "인사":
    answer_text = test.find_one({"Intent": "인사"})['Answer']

elif intent_name == "욕설":
    answer_text = test.find_one({"Intent": "욕설"})['Answer']


# 날짜, 강의실 정보가 모두 입력되었을 때
elif intent_name == "강의실" and "B_ROOM" in ner_tags and "B_DT" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_ROOM, B_DT"})['Answer']
    # 인식된 태그를 입력한 단어로 변환
    # 답변을 출력할 수 있도록 변수와 리스트에 저장
    for word, tag in predicts:
        if tag == "B_ROOM":
            place.append(word)
        if tag == "B_DT":
            time.append(word)
    # print(place, time) # 입력된 장소 정보와 시간 정보
    # 오늘 이라는 값을 리스트에 넣어 확인하려 했는데 그럼 for 하나 더 써야 해서 그냥 이렇게 함
    if '오늘' or '지금' or '현재' in time: # 오늘 강의실 정보를 요청하는 거라면
        # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
        # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
        place = "차235"
        # room, time 을 다영이 정보로 변환하기
        if db.info.find_one({'room': place}):
            class_time = db.info.find_one({'room': place})['time']
            new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
            # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
            class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
        print(class_list)
    else:
        pass
        # time에 저장된 날짜로 검색하면 된다

# 강의실 정보만 입력되었을 때, 날짜 정보는 입력 안됨
# 오늘을 기준으로 돌리면 된다
elif intent_name == "강의실" and "B_ROOM" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_ROOM"})['Answer']
    for word, tag in predicts:
        if tag == "B_ROOM":
            place = word
        # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
        # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
    place = "차235"
    # room, time 을 다영이 정보로 변환하기
    if db.info.find_one({'room': place}):
        class_time = db.info.find_one({'room': place})['time']
        new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
        # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
        class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
    print(class_list)


# 날짜 정보만 입력되고 강의실 정보는 입력되지 않았을 때
# 강의실 정보를 한번 더 물어보기
elif intent_name == "강의실" and "B_DT" in ner_tags:
    answer_text = test.find_one({"Intent": "강의실", "NER": "B_DT"})['Answer']

    # answer_text = test.find_one({"Intent": "강의실"}, {"NER": "B_ROOM"})['Answer']
    # print(answer_text)

elif intent_name == "강의실" and "B_DT" not in ner_tags and "B_ROOM" not in ner_tags:
    answer_text = test.find_one({"Intent": "강의실"})['Answer']

try:
    pass
    # if intent_name == "강의실" and "B_ROOM" in ner_tags:
    #     answer_text = test.find_one({"의도(Intent)":"강의실"})['답변(Answer)']
    #     print(answer_text)

except:
    answer_text = "죄송합니다. 이해하지 못했어요 다시 한번 말씀해주세요"

print("답변 : ", answer_text)