import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from pathlib import Path
from Chatbot.config import api_key, chat_id
from pymongo import MongoClient
from DataBase.config import MONGO_URL
from Chatbot.get_time import get_weekday, get_now_time, get_next_day, get_n_day_weekday
from datetime import datetime, time
import tensorflow as tf
from Model.Preprocess import Preprocess
from Model.NerModel import NerModel
from Model.IntentModel import IntentModel
from hanspell import spell_checker  # 1011 맞춤법 검사기 추가
from Find_Answer import find_answer1, find_answer2  # 1012 중복코드 함수화

BASE_DIR = Path(__file__).resolve().parent

client = MongoClient(MONGO_URL)
db = client['DS']
bot = telegram.Bot(token=api_key)
answer = db.answer  # 답변 출력

# 1006 model 추가/ 1010 의도, 개체명을 바탕으로 답변 출력
# 전처리 객체 생성
p = Preprocess(word2index_dic='./Model/chatbot_dict.bin', userdic='./Model/user_dic.tsv')
# 의도 파악
intent = IntentModel(model_name='./Model/intent_model_2.h5', proprocess=p)

# 개체명 인식
ner = tf.keras.models.load_model('./Model/ner_model.h5')

info_message = '''
공강이 에게 빈 강의실 정보를 물어봐보세요. 

- 지금 사용할 수 있는 빈 강의실을 알고 싶다면 : 지금 + <사용할 강의실 이름>
- 나중에 사용할 수 있는 빈 강의실을 알고 싶다면 : 사용할 날짜(형식: n월 n일) + <사용할 강의실 이름>
example1) 지금 차235 비었어?
example2) 10월 25일 차320 사용가능해?
'''


def start(update, context):
    bot.send_message(chat_id, text='안녕하세요! 저는 덕성여대 빈 강의실 정보를 알려주는 송강이 아닌 공강이 챗봇입니다.')  # 사용자가 채팅방에 입장시 인사말
    bot.send_message(chat_id=update.effective_chat_id, text=info_message)


# updater
updater = Updater(token=api_key, use_context=True)
dispatcher = updater.dispatcher
# 주기적으로 텔레그램 서버에 접속 해 chatbot 으로부터 새로운 메시지가 존재하면 받아오는 명령어
updater.start_polling()


def handler(update, context):
    global mon_split, day_split
    user_text = update.message.text  # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    print("입력받은 문장:", user_text)

    # 맞춤법 검사
    spelled_sent = spell_checker.check(user_text)
    user_text = spelled_sent.checked

    predict = intent.predict_class(user_text)
    intent_name = intent.labels[predict]

    # 모델 돌릴때 추가적으로 필요한 코드 (model_test.py 파일 코드)
    # 의도 파악
    predict = intent.predict_class(user_text)
    intent_name = intent.labels[predict]

    # 개체명 인식
    ner = NerModel(model_name='./Model/ner_model.h5', proprocess=p)
    predicts = ner.predict(user_text)
    ner_tags = ner.predict_tags(user_text)

    print("질문 : ", user_text)
    print("=" * 100)
    print("의도 파악 : ", intent_name)
    print("개체명 인식 : ", predicts)
    print("답변 검색에 필요한 NER 태그 : ", ner_tags)
    print("=" * 100)

    # 답변 검색- chatbot_test.py 파일 코드
    class_time = []
    place = []

    try:  # 1012 모델 완성전 예외처리
        if intent_name == "기타":
            answer_text = answer.find_one({"Intent": "기타"})['Answer']
            print("답변 : ", answer_text)


        elif intent_name == "인사":
            answer_text = answer.find_one({"Intent": "인사"})['Answer']
            print("답변 : ", answer_text)


        # 시간, 강의실 정보가 모두 입력 되었을 때
        elif intent_name == "강의실" and "B_ROOM" in ner_tags and "B_TIME" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_ROOM, B_TIME"})['Answer']
            # 인식된 태그를 입력한 단어로 변환
            # 답변을 출력할 수 있도록 변수와 리스트에 저장
            for word, tag in predicts:
                if tag == "B_ROOM":
                    place.append(word)
                if tag == "B_TIME":
                    class_time.append(word)
            # print(place, time) # 입력된 장소 정보와 시간 정보
            # 오늘 이라는 값을 리스트에 넣어 확인하려 했는데 그럼 for 하나 더 써야 해서 그냥 이렇게 함
            if '오늘' or '지금' or '현재' in class_time:  # 오늘 강의실 정보를 요청하는 거라면
                # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
                # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
                place = "차235"
                # room, time 을 다영이 정보로 변환하기

                find_answer1(place)

                class_list, new_class_time = find_answer1(place)

                find_answer2(class_list, new_class_time)

                start_time_list, end_time_list, lec_time_list = find_answer2(class_list, new_class_time)

                # 수업중 인지 아닌지 출력
                break_flag = True  # 이중 for문 빠져나옴
                for start_time_index in start_time_list:
                    for end_time_index in end_time_list:
                        if start_time_index <= get_now_time() <= end_time_index:
                            bot.send_message(chat_id, text=f"입력 하신 {place} 은 현재 수업중입니다.")
                            break_flag = False
                            break
                        else:
                            bot.send_message(chat_id,
                                             text=f"입력 하신 {place} 의 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 "
                                                  f"가능 합니다.")
                            break_flag = False
                            break
                    if not break_flag:
                        break

            else:
                pass
                # time에 저장된 날짜로 검색하면 된다

        # 날짜, 강의실 정보가 모두 입력 되었을 때
        elif intent_name == "강의실" and "B_ROOM" in ner_tags and "B_DAY" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_ROOM, B_DAY"})['Answer']
            # 인식된 태그를 입력한 단어로 변환
            # 답변을 출력할 수 있도록 변수와 리스트에 저장
            for word, tag in predicts:
                if tag == "B_ROOM":
                    place.append(word)
                if tag == "B_DAY":
                    class_time.append(word)
                # print(place, time) # 입력된 장소 정보와 시간 정보
                # 오늘 이라는 값을 리스트에 넣어 확인하려 했는데 그럼 for 하나 더 써야 해서 그냥 이렇게 함
                # if '오늘' or '지금' or '현재' in time:  # 오늘 강의실 정보를 요청하는 거라면
                #     # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
                #
                #     # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
                #     place = "차235"
                #
                #     # room, time 을 다영이 정보로 변환하기
                #     find_answer1(place)
                #     if db.info.find_one({'강의실': place}):
                #         class_time = db.info.find_one({'강의실': place})['강의시간']
                #         new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
                #         # print(new_class_time)  # 금C~D,목F,수C~D,수F,월D,월E,화D
                #         class_list = new_class_time.split(',')  # 문자열 to 리스트 자료형으로 변경
                #         print(class_list)
                # else:
                #     # pass
                # time에 저장된 날짜로 검색하면 된다

                # test
                # time = ["10월 19일"]

                for i in class_time:
                    mon_split = i.split("월")

                print(mon_split[0])
                mon = int(mon_split[0])

                for j in mon_split:
                    day_split = j.split("일")

                print(day_split[0].replace(" ", ""))  # str
                day = int(day_split[0].replace(" ", ""))

                test = datetime(2022, mon, day)
                n_day = get_next_day(test)

                class_list, new_class_time = find_answer1(place)

                start_time_list, end_time_list, lec_time_list = find_answer2(class_list, new_class_time)

                # if db.inform.find_one({'강의실': place}):
                #     class_time = db.inform.find_one({'강의실': place})['강의시간']
                #     new_class_time = class_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
                #     # print(new_class_time)
                #     class_list = new_class_time.split(',')  # 리스트 자료형
                #
                #
                # test = []
                # alpha_list = []
                # lec_time_list = []
                # if get_n_day_weekday(n_day) in new_class_time:
                #     # 리스트의 인덱스를 찾은 후 알파벳을 찾아 디비의 정보와 비교
                #     for i in range(len(class_list)):
                #         if get_n_day_weekday(n_day) in class_list[i]:
                #             test.append(class_list[i])
                #     for i in test:
                #         if len(i) == 4:
                #             for j in range(len(i)):
                #                 if j == 1:
                #                     alpha_list.append(i[j])
                #                 elif j == 3:
                #                     alpha_list.append(i[j])
                #         elif len(i) == 2:
                #             for l in range(len(i)):
                #                 if l == 1:
                #                     alpha_list.append(i[l])
                #
                #     for a in alpha_list:
                #         lec_time = db.inform.find_one({'교시': a})['시간']
                #         lec_time_list.append(lec_time)
                #     for s in lec_time_list:
                #         print('s is', s)
                bot.send_message(chat_id,
                                 text=f"입력 하신 {n_day} 의 {place} 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 가능 합니다.")


        # 강의실 정보만 입력되었을 때, 날짜 정보는 입력 안됨
        # 오늘을 기준으로 돌리면 된다
        elif intent_name == "강의실" and "B_ROOM" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_ROOM"})['Answer']
            for word, tag in predicts:
                if tag == "B_ROOM":
                    place = word
                # print('get_now_time: ', get_now_time())  # 현재 시간 - 여기에는 없어서 일단 주석
                # 임시로 place 할당 - 인식률 높아지면 변경하면 된다
            place = "차235"
            # room, time 을 다영이 정보로 변환하기
            class_list, new_class_time = find_answer1(place)

            start_time_list, end_time_list, lec_time_list = find_answer2(class_list, new_class_time)
            # 수업중 인지 아닌지 출력
            break_flag = True  # 이중 for문 빠져나옴
            for start_time_index in start_time_list:
                for end_time_index in end_time_list:
                    if start_time_index <= get_now_time() <= end_time_index:
                        bot.send_message(chat_id, text=f"입력 하신 {place} 은 현재 수업중입니다.")
                        break_flag = False
                        break
                    else:
                        bot.send_message(chat_id,
                                         text=f"입력 하신 {place} 의 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 "
                                              f"가능 합니다.")
                        break_flag = False
                        break
                if not break_flag:
                    break



        # 시간 정보만 입력되고 강의실 정보는 입력되지 않았을 때
        # 강의실 정보를 한번 더 물어보기
        elif intent_name == "강의실" and "B_TIME" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_TIME"})['Answer']
            print("답변 : ", answer_text)

            # answer_text = test.find_one({"Intent": "강의실"}, {"NER": "B_ROOM"})['Answer']
            # print(answer_text)
        elif intent_name == "강의실" and "B_DAY" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_DAY"})['Answer']
            print("답변 : ", answer_text)

        elif intent_name == "강의실" and "B_TIME" not in ner_tags and "B_ROOM" not in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실"})['Answer']
            print("답변 : ", answer_text)
        elif intent_name == "강의실" and "B_DAY" not in ner_tags and "B_ROOM" not in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실"})['Answer']
            print("답변 : ", answer_text)

        try:
            pass
            # if intent_name == "강의실" and "B_ROOM" in ner_tags:
            #     answer_text = test.find_one({"의도(Intent)":"강의실"})['답변(Answer)']
            #     print(answer_text)

        except:
            answer_text = "죄송합니다. 이해하지 못했어요. 다시 한번 말씀해주세요"
            print("답변 : ", answer_text)
            time.sleep(1)

    except Exception as e:
        # pass
        answer_text = "죄송합니다. 이해하지 못했어요. 다시 한번 말씀해주세요"
        print("답변 : ", answer_text)

    if '뭐' in user_text:  # 맞춤법 검사; 뭐해? -> 뭐 해?로 인식
        bot.send_message(chat_id, text='자연어 처리에 대해 공부중이에요.')  # 답장보내기
    elif '누구야' in user_text:
        bot.send_message(chat_id, text='저는 덕성여대 빈 강의실 정보를 알려주는 송강이 아닌 공강이 챗봇입니다 😄')
    elif '누가' in user_text:
        bot.send_message(chat_id, text='저는 소프트웨어 캡스톤 디자인의 유니콘팀에 의해 만들어졌어요~ 🤖')
    else:
        bot.send_message(chat_id, text='아직 수집되지 않은 정보에요.')


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text,
                              handler)  # chatbot에게  메세지를 전송하면,updater를 통해 필터링된 text가 handler로 전달이 된다. -> 가장 중요하고, 계속해서 수정할 부분

dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
