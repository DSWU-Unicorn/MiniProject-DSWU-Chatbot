import telegram
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from pathlib import Path
from Chatbot.config import api_key, chat_id
from pymongo import MongoClient
from DataBase.config import MONGO_URL
from Chatbot.get_time import get_weekday, get_now_time, get_next_day, get_n_day_weekday
from datetime import datetime

# import datetime
BASE_DIR = Path(__file__).resolve().parent

client = MongoClient(MONGO_URL)
db = client['DS']
bot = telegram.Bot(token=api_key)
answer = db.answer  # 답변 출력


def find_answer1(place):
    global class_list, new_class_time
    print('find_answer1:', place)

    if db.inform.find_one({'강의실': place}):
        lec_time = db.inform.find_one({'강의실': place})['강의시간']
        print('lec_time:', lec_time)
        new_class_time = lec_time.replace("'", '').replace("[", '').replace("]", '').replace(" ", '')
        class_list = new_class_time.split(',')
        print('class_list', class_list)  # 금C~D,목F,수C~D,수F,월D,월E,화D

    return class_list, new_class_time


def find_answer2(class_list, new_class_time):
    global start_time_list, end_time_list
    today_lec_time = []
    alpha_list = []  # 강의 교시인 알파벳 추출
    lec_time_list = []

    if get_weekday() in new_class_time:  # 강의 시간 중 오늘 요일이 있다면
        # 리스트의 인덱스와 강의 시간을 찾아 디비의 강의 시간 정보와 비교
        for i in range(len(class_list)):
            if get_weekday() in class_list[i]:
                today_lec_time.append(class_list[i])
        print('today_lec_time: ', today_lec_time)

        for lec_time in today_lec_time:
            if len(lec_time) == 4:
                for j in range(len(lec_time)):
                    if j == 1:
                        alpha_list.append(lec_time[j])
                    elif j == 3:
                        alpha_list.append(lec_time[j])
            elif len(lec_time) == 2:
                for k in range(len(lec_time)):
                    if k == 1:
                        alpha_list.append(lec_time[k])

        for a in alpha_list:
            lec_time = db.inform.find_one({'교시': a})['시간']
            lec_time_list.append(lec_time)
        # print('lec_time_list :', lec_time_list)

        # 1005 사용자가 입력한 시간과 시간표의 수업 시간이 일치할 때 코드 작성
        start_time_list = []
        end_time_list = []
        for s in lec_time_list:
            start_time = datetime.strptime((str(s.split('-')[0])), '%H:%M')
            end_time = datetime.strptime((str(s.split('-')[1])), '%H:%M')
            start_time_list.append(start_time.strftime('%H:%M'))
            end_time_list.append(end_time.strftime('%H:%M'))

    return start_time_list, end_time_list, lec_time_list


def find_answer3(class_list, new_class_time, n_day):
    test = []
    alpha_list = []
    lec_time_list = []
    if get_n_day_weekday(n_day) in new_class_time:
        # 리스트의 인덱스를 찾은 후 알파벳을 찾아 디비의 정보와 비교
        for i in range(len(class_list)):
            if get_n_day_weekday(n_day) in class_list[i]:
                test.append(class_list[i])

        for i in test:
            if len(i) == 4:
                for j in range(len(i)):
                    if j == 1:
                        alpha_list.append(i[j])
                    elif j == 3:
                        alpha_list.append(i[j])
            elif len(i) == 2:
                for l in range(len(i)):
                    if l == 1:
                        alpha_list.append(i[l])

        for a in alpha_list:
            lec_time = db.inform.find_one({'교시': a})['시간']
            lec_time_list.append(lec_time)
    else:  # 주말이라면
        return False
    return lec_time_list


def find_n_day(class_time):
    global day_split
    mon_split = class_time.split("월")

    mon = int(mon_split[0])

    for j in mon_split:
        day_split = j.split("일")

    day = int(day_split[0].replace(" ", ""))

    test = datetime(2022, mon, day)
    n_day = get_next_day(test)
    return n_day
