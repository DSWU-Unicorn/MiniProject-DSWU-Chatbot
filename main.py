import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from pathlib import Path
from Chatbot.config import api_key, chat_id
from pymongo import MongoClient
from DataBase.config import MONGO_URL, MONGO_DB_NAME
from Chatbot.get_time import get_weekday, get_now_time
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
# print('base dir is..', BASE_DIR)

client = MongoClient(MONGO_URL)
db = client['DS']
bot = telegram.Bot(token=api_key)

info_message = '''
공강이에게 빈 강의실 정보를 물어봐보세요. 

- 지금 사용할 수 있는 빈 강의실을 알고 싶다면 : 지금 + <사용할 건물 이름>
- 나중에 사용할 수 있는 빈 강의실을 알고 싶다면 : 사용할 날짜와 시간 +  사용할 건물의 강의실 명
example1) 지금 차235 비었어?
example2) 오늘 2시 차320 쓸 수 있어?
'''


def start(update, context):
    bot.send_message(chat_id, text='안녕하세요! 덕성여대 차관의 빈 강의실 정보를 알려주는 저는 송강이 아닌 공강이 챗봇입니다.')  # 채팅방 입장시 인사말
    bot.send_message(chat_id=update.effective_chat_id, text=info_message)


# updater
updater = Updater(token=api_key, use_context=True)
dispatcher = updater.dispatcher
# 주기적으로 텔레그램 서버에 접속 해 chatbot 으로부터 새로운 메시지가 존재하면 받아오는 명령어
updater.start_polling()


def handler(update, context):
    user_text = update.message.text  # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    # chat_id= update.message.chat_id

    if '뭐해' in user_text:
        bot.send_message(chat_id, text='자연어 처리에 대해 공부중이에요.')  # 답장보내기
    elif '지금' in user_text:  # 지금(v)차235(v)비었어? # 띄어쓰기 필수
        print(get_now_time())
        place = user_text.split()[1]

        if db.inform.find_one({'강의실': place}):
            class_time = db.inform.find_one({'강의실': place})['강의시간']
            class_list = class_time.split(',')
            print(type(class_list))

            if get_weekday() in class_time: # 문자열
                print('class_list is..', class_list)
                # 0930
                # 리스트의 인덱스를 찾은 후 알파벳을 찾아 디비의 정보와 비교할 예정

                class_time.index('')


            # bot.send_message(chat_id, get_weekday())

            bot.send_message(chat_id, text='현재 차관 빈강의실은 000, 000, 000 입니다.')
    else:
        bot.send_message(chat_id, text='수집되지 않은 정보입니다.')


start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text,
                              handler)  # chatbot에게 메세지를 전송하면,updater를 통해 필터링된 text가 handler로 전달이 된다. -> 가장 중요하고, 계속해서 수정할 부분

dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
