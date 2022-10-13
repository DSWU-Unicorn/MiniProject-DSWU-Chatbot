# 0928
import time
import datetime

from pyasn1.compat.dateandtime import strptime

now = datetime.datetime.now()


# 채팅이 들어오면 날짜, 시간을 파악해서 데이터베이스에 있는 정보를 뽑아준다.
def get_now_time():
    return now.strftime('%H:%M')


def get_now_date():
    return now.strftime('%Y-%m-%d')


# 오늘 차관 빈 강의실 있어? 와 같은 구체적인 시간이 없는 발화일 때
def get_weekday():
    if now.strftime('%Y-%m-%d %H:%M'):
        if now.weekday() == 0:  # Mon
            return '월'
        if now.weekday() == 1:  # Tues
            return '화'
        if now.weekday() == 2:
            return '수'
        if now.weekday() == 3:
            return '목'
        if now.weekday() == 4:
            return '금'
            # 현재 시간 기준으로 빈 강의실 정보를 어떻게 뿌릴지 고ㅑ
        elif now.weekday() == 5 or now.weekday() == 6:  # weekend
            return '주말'


def get_n_day_weekday(n_day):
    n_day = strptime(n_day, '%Y.%m.%d')
    if n_day.weekday() == 0:
        return '월'
    if n_day.weekday() == 1:
        return '화'
    if n_day.weekday() == 2:
        return '수'
    if n_day.weekday() == 3:
        return '목'
    if n_day.weekday() == 4:
        return '금'
    elif n_day.weekday() == 5 or n_day.weekday() == 6:  # weekend
        return '주말'


def get_next_day(string):  # 후 일자
    day_cnt = (string - now)

    # print("day_cnt:", day_cnt)
    future_day = now + day_cnt
    if future_day.month < 10:
        month = '0' + str(future_day.month)
    else:
        month = str(future_day.month)
    if future_day.day < 10:
        day = '0' + str(future_day.day)
    else:
        day = str(future_day.day)

    next_day = str(future_day.year) + '.' + month + '.' + day
    return next_day


def get_after_day(few_day):
    tomorow = datetime.date.today() + datetime.timedelta(days=few_day)
    tomorow = tomorow.strftime('%Y.%m.%d')
    return tomorow
