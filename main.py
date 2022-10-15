import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from pathlib import Path
from Chatbot.config import api_key, chat_id
from pymongo import MongoClient
from DataBase.config import MONGO_URL
from Chatbot.get_time import get_weekday, get_now_time, get_next_day, get_n_day_weekday, get_after_day
from datetime import datetime
import datetime
import time
import tensorflow as tf
from Model.Preprocess import Preprocess
from Model.NerModel import NerModel
from Model.IntentModel import IntentModel
from hanspell import spell_checker  # 1011 맞춤법 검사기 추가
from Find_Answer import find_answer1, find_answer2, find_n_day, find_answer3  # 1012 중복코드 함수화

BASE_DIR = Path(__file__).resolve().parent

client = MongoClient(MONGO_URL)
db = client['DS']
bot = telegram.Bot(token=api_key)
answer = db.answer  # 답변 출력

# 1006 model 추가/ 1010 의도, 개체명을 바탕으로 답변 출력
# 1013
# 전처리 객체
p_intent = Preprocess(word2index_dic='./Model/chatbot_dict_intent.bin', userdic='./Model/user_dic_intent.tsv')
p_ner = Preprocess(word2index_dic='./Model/chatbot_dict_ner.bin',
                   userdic='./Model/user_dic_ner.tsv')

# 의도 파악
intent = IntentModel(model_name='./Model/intent_model_2.h5', proprocess=p_intent)

# 개체명 인식
ner = NerModel(model_name='./Model/ner_model.h5', proprocess=p_ner)

# ner = tf.keras.models.load_model('./Model/ner_model.h5')

info_message = '''
🤖공강이 에게 빈 강의실 정보를 물어봐보세요. 

- 지금 사용할 수 있는 빈 강의실을 알고 싶다면
    <오늘 차 235 어디서 공부할 수 있나요> 처럼 물어봐보세요. 
- 나중에 사용할 수 있는 빈 강의실을 알고 싶다면
    <10월 21일 320 언제 사용 가능해?> 처럼 물어봐보세요.
'''


def start(update, context):
    bot.send_message(chat_id, text='안녕하세요!')  # 사용자가 채팅방에 입장시 인사말
    bot.send_message(chat_id=update.effective_chat_id, text=info_message)


# updater
updater = Updater(token=api_key)
dispatcher = updater.dispatcher
# 주기적으로 텔레그램 서버에 접속 해 chatbot 으로부터 새로운 메시지가 존재하면 받아오는 명령어
updater.start_polling()


def handler(update, context):
    global mon_split, day_split, word
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
    predicts = ner.predict(user_text)
    ner_tags = ner.predict_tags(user_text)

    print("질문 : ", user_text)
    print("=" * 100)
    print("의도 파악 : ", intent_name)
    print("개체명 인식 : ", predicts)
    print("답변 검색에 필요한 NER 태그 : ", ner_tags)
    print("=" * 100)

    class_time = ""
    place = ""
    lecture_time = []

    try:  # 예외처리
        if '뭐' in user_text:  # 맞춤법 검사; 뭐해? -> 뭐 해?로 인식
            bot.send_message(chat_id, text='자연어 처리에 대해 공부중이에요.')  # 답장보내기
        elif '누구야' in user_text:
            bot.send_message(chat_id, text='저는 덕성여대 빈 강의실 정보를 알려주는 송강이 아닌 공강이 챗봇입니다 😄')
        elif '누가' in user_text:
            bot.send_message(chat_id, text='저는 소프트웨어 캡스톤 디자인의 유니콘팀에 의해 만들어졌어요~ 🤖')
        elif intent_name == "인사":
            answer_text = answer.find_one({"Intent": "인사"})['Answer']
            print("답변 : ", answer_text)
            bot.send_message(chat_id, text=f'{answer_text}')

        # 시간, 강의실 정보가 모두 입력 되었을 때
        elif intent_name == "강의실" and "B_ROOM" in ner_tags and "B_DT" in ner_tags:
            # 인식된 태그를 입력한 단어로 변환
            # 답변을 출력할 수 있도록 변수와 리스트에 저장
            for word, tag in predicts:
                if tag == "B_ROOM":
                    place = '차' + word
                    print('place: ', place)

                if tag == "B_DT":
                    class_time = word
                    lecture_time.append(class_time)

            if place == '차차미리사':  # 차미리사는 광범위함, 좁혀서 강의실 정보 요청
                answer_text = answer.find_one({"Intent": "강의실", "NER": "B_DT"})['Answer']
                print("답변 : ", answer_text)
                bot.send_message(chat_id, text=f'{answer_text}')

            else:
                answer_text = answer.find_one({"Intent": "강의실", "NER": "B_ROOM, B_DT"})['Answer']
                bot.send_message(chat_id, text=f'{answer_text}')

                for t in lecture_time:
                    if t == '내일':
                        tomorrow = get_after_day(1)
                        class_list, new_class_time = find_answer1(place)
                        lec_time_list = find_answer3(class_list, new_class_time, tomorrow)

                        if not bool(find_answer3(class_list, new_class_time, tomorrow)):
                            bot.send_message(chat_id,

                                             text=f"입력 하신 {tomorrow} 의 {place} 강의 시간은 없습니다. 해당 날짜는 주말입니다.")
                            break
                        bot.send_message(chat_id,
                                         text=f"입력 하신 {tomorrow} 의 {place} 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 가능 합니다.")
                        break
                    if t == '모레':  # 2일후
                        tomorrow = get_after_day(2)
                        class_list, new_class_time = find_answer1(place)

                        lec_time_list = find_answer3(class_list, new_class_time, tomorrow)

                        if not bool(find_answer3(class_list, new_class_time, tomorrow)):
                            bot.send_message(chat_id,
                                             text=f"입력 하신 {tomorrow} 의 {place} 강의 시간은 없습니다. 해당 날짜는 주말입니다.")
                            break
                        bot.send_message(chat_id,
                                         text=f"입력 하신 {tomorrow} 의 {place} 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 가능 합니다.")
                        break

                    if '월' in t:  # month, n월 n일 입력시
                        class_list, new_class_time = find_answer1(place)

                        n_day = find_n_day(class_time)
                        lec_time_list = find_answer3(class_list, new_class_time, n_day)

                        if not bool(find_answer3(class_list, new_class_time, n_day)):
                            bot.send_message(chat_id,
                                             text=f"입력 하신 {n_day} 의 {place} 강의 시간은 없습니다. 해당 날짜는 주말입니다.")
                            break
                        bot.send_message(chat_id,
                                         text=f"입력 하신 {n_day} 의 {place} 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 가능 합니다.")
                        break
                    if t == '오늘' or t == '지금' or t == '현재':
                        class_list, new_class_time = find_answer1(place)
                        start_time_list, end_time_list, lec_time_list = find_answer2(class_list, new_class_time)

                        # 수업중 인지 아닌지 출력
                        break_flag = True  # 이중 for문 빠져나옴
                        for start_time_index in start_time_list:
                            for end_time_index in end_time_list:
                                if start_time_index <= get_now_time() <= end_time_index:
                                    bot.send_message(chat_id, text=f"입력 하신 {place} 은 현재 수업중입니다.")
                                    bot.send_message(chat_id,
                                                     text=f"입력 하신 {place} 의 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 "
                                                          f"가능 합니다.")
                                    break_flag = False
                                    break
                                else:
                                    answer_text = answer.find_one({"Intent": "강의실", "NER": "B_ROOM, B_DT"})['Answer']
                                    bot.send_message(chat_id, text=f'{answer_text}')
                                    bot.send_message(chat_id,
                                                     text=f"입력 하신 {place} 의 강의 시간은 {lec_time_list} 입니다. 이를 제외한 시간은 빈 강의실로 사용 "
                                                          f"가능 합니다.")
                                    break_flag = False
                                    break
                            if not break_flag:
                                break



        # 강의실 정보만 입력되었을 때, 날짜 정보는 입력 안됨
        # 오늘을 기준으로 빈 강의실 정보 출력
        elif intent_name == "강의실" and "B_ROOM" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_ROOM"})['Answer']
            for word, tag in predicts:
                if tag == "B_ROOM":
                    place = '차' + word

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
        elif intent_name == "강의실" and "B_DT" in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실", "NER": "B_DT"})['Answer']
            print("답변 : ", answer_text)
            bot.send_message(chat_id, text=f'{answer_text}')


        elif intent_name == "강의실" and "B_DT" not in ner_tags and "B_ROOM" not in ner_tags:
            answer_text = answer.find_one({"Intent": "강의실"})['Answer']
            print("답변 : ", answer_text)
            bot.send_message(chat_id, text=f'{answer_text}')

        elif intent_name == "기타":
            answer_text = answer.find_one({"Intent": "기타"})['Answer']
            print("답변 : ", answer_text)
            bot.send_message(chat_id, text=f'{answer_text}')

        try:
            pass

        except:
            answer_text = "죄송합니다. 이해하지 못했어요. 다시 한번 말씀해주세요"
            print("답변 : ", answer_text)
            time.sleep(1)

    except ConnectionResetError as e:
        print("텔레그램에서 응답이 없습니다.")
        time.sleep(1)


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text,
                              handler)  # chatbot에게  메세지를 전송하면,updater를 통해 필터링된 text가 handler로 전달이 된다. -> 가장 중요하고, 계속해서 수정할 부분

dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
