# 0928
from datetime import datetime, timedelta

now = datetime.now()

# 채팅이 들어오면 날짜, 시간을 파악해서 데이터베이스에 있는 정보를 뽑아준다.
# print("현재 날짜 : ", now.date())
# print("현재 시간 : ", now.time())  # 24 시간제
#
# print("년 : ", now.year)
# print("월 : ", now.month)
# print("일 : ", now.day)
# print("시 : ", now.hour)
# print("분 : ", now.minute)
def get_now_time():
    return now.strftime('%H:%M')

print(get_now_time())

lecture_room = [235, 320]


# 오늘 차관 빈 강의실 있어? 와 같은 구체적인 시간이 없는 발화일 때
def get_weekday():
    if now.strftime('%Y-%m-%d %H:%M'):
        if now.weekday() == 0:  # Mon
            # if 월요일 빈 강의실 in db:
            return '월'

            # db에서 월요일의 차관 빈 강의실들을 가져온다
            # (f"월요일인 오늘 차관의 빈 강의실은 {lecture_room} 입니다!")
            # else:
            # ("월요일인 오늘 차관의 빈 강의실은 없습니다!")

        if now.weekday() == 1:  # Tues
            return '화'
            # if 화요일 빈 강의실 in db:
            # print(f"화요일인 오늘 차관의 빈 강의실은 {lecture_room} 입니다!")
            # else:
            # print("화요일인 오늘 차관의 빈 강의실은 없습니다!")
        if now.weekday() == 2:
            return '수'
            # if 수요일 빈 강의실 in db:
            # return (f"수요일인 오늘 차관의 빈 강의실은 {lecture_room} 입니다!")
            # else:
            # print("수요일인 오늘 차관의 빈 강의실은 없습니다!")
        if now.weekday() == 3:
            return '목'
            # if 목요일 빈 강의실 in db:
            # print(f"목요일인 오늘 차관의 빈 강의실은 {lecture_room} 입니다!")
            # else:
            # print("목요일인 오늘 차관의 빈 강의실은 없습니다!")
        if now.weekday() == 4:
            return '금'
            # if 금요일 빈 강의실 in db:
            # 0930
            #if now_time
            # 현재 시간 기준으로 빈 강의실 정보를 어떻게 뿌릴지 고ㅑ
            # print(f"금요일인 오늘 차관의 빈 강의실은 {lecture_room} 입니다!")
            # else:
            # print("금요일인 오늘 차관의 빈 강의실은 없습니다!")
        elif now.weekday() == 5 or now.weekday() == 6:  # weekend
            return '주말'
            # print(f"주말인 오늘 차관의 빈 강의실은 {lecture_room} 입니다!")

get_weekday()
# 구체적으로 어떤 강의실이 언제 비는지 물어볼때.. 코드 짜야됨


day_list = {'내일': 1, '모레': 2}  # string, day_cnt


# 내일, 모레...등의 데이터가 들어왔을때 오늘로부터 미래의 날짜 구하기

def get_next_day(string, day_cnt):  # 오늘 날짜, 이동할 날짜 수
    date = now.strptime(string, '%Y-%m-%d')
    future_day = date + timedelta(days=day_cnt)
    if future_day.month < 10:
        month = '0' + str(future_day.month)
    else:
        month = str(future_day.month)

    if future_day.day < 10:

        day = '0' + str(future_day.day)
    else:

        day = str(future_day.day)

    after_day = str(future_day.year) + '.' + month + '.' + day
    return after_day

print(get_next_day(now.strftime('%Y-%m-%d'), 7))
