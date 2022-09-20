# 22.09.20 id 가져오는 코드
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
BASE_DIR = Path(__file__).resolve().parent

url = "https://discover.duksung.ac.kr/pyxis-api/1/bulletin-boards/1/bulletins?max=100&nameOption=hide&offset=0"
payload={}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
res=response.json()
# print(res)

lib_dic={'id':[], 'content':[]}

id_list= []
try:
    for item in res["data"]['list']:
    # ['id']
        id_list.append(item['id'])
except:
    time.sleep(2)

print(id_list) # id 저장

# 내부 url
for id in id_list:
    url = f"https://discover.duksung.ac.kr/pyxis-api/1/bulletins/{id}"

    querystring = {"nameOption":"hide"}

    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)
    con_res = response.json()

    print(con_res)
    con_list = []
    try:
        for content in con_res["data"]['content']:
            #regex = "\(.*\)|\ㄴ-\ㄴ.*"
            #cleanr = re.compile('<.*?>')
            #cleantext = BeautifulSoup(content, "lxml").text
            new_str = re.sub(r"[^\uAC00-\uD7A30-9가-힣]", "", content)

            new_str = new_str.strip('돋움')
            new_str = new_str.strip('함초롬바탕')
            new_str = new_str.strip('굴림')
            new_str = new_str.strip('한컴윤고딕')
            new_str = new_str.strip('함초롬돋움')
            new_str = new_str.strip('맑은고딕')
            new_str.lstrip()
            new_str.rstrip()
            #cleantext = re.sub(cleanr, '', cleantext)
            con_list.append(new_str)

        # print(con_list)
        notice=''.join(con_list)
        # 연속된 숫자 삭제 -> 로직어떻게하지?
        # 053579899502022916금온라인으로진행된이용교육입니다계정생성부터문헌수집인용삽입및참문헌목록생성을포하였으며교육시간약1시간입니다 이렇게 있을때, 연속된 3자리 이상의 숫자를 삭제하고픔.
        print(notice)
        lib_dic['id'].append(id)
        lib_dic['content'].append(notice)


    except:
        time.sleep(2)

pd.DataFrame(lib_dic).to_csv(BASE_DIR/'crawling_library_notice_content.csv', encoding='utf-8-sig')
print('crawling_library_notice_content.csv done!')



