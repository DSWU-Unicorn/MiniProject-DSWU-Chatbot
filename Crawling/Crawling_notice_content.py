# 22.09.20 id 가져오는 코드
import re
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent

url = "https://discover.duksung.ac.kr/pyxis-api/1/bulletin-boards/1/bulletins?max=100&nameOption=hide&offset=0"
payload = {}
headers = {}
response = requests.request("GET", url, headers=headers, data=payload)
res = response.json()
# print(res)

lib_dic = {'id': [], 'content': []}

id_list = []
try:
    for item in res["data"]['list']:
        # ['id']
        id_list.append(item['id'])
except:
    time.sleep(2)

# print(id_list)  # id 저장

# 내부 url
for id in id_list:
    url = f"https://discover.duksung.ac.kr/pyxis-api/1/bulletins/{id}"

    querystring = {"nameOption": "hide"}

    payload = ""
    response = requests.request("GET", url, data=payload, params=querystring)
    con_res = response.json()

    con_list = []
    try:
        for content in con_res["data"]['content']:
            # regex = "\(.*\)|\ㄴ-\ㄴ.*"
            # cleanr = re.compile('<.*?>')
            # cleantext = BeautifulSoup(content, "lxml").text
            '''
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
            '''
            con_list.append(content)
        # print(con_list)
        notice = ''.join(con_list)

        html_tag = re.compile('<.*?>')
        text = re.sub(html_tag, '', notice)
        text = text.replace('&nbsp;', '')
        text = text.replace('&amp;', '')
        text = text.replace('&quot;', '')
        text = text.replace('&lt;', '')
        text = text.replace('&gt;', '')
        text = text.replace('&darr;', '')
        text = text.replace('&#39;', '')
        text = text.replace('&#39;', '')
        text = text.replace('&rarr;', '')
        text = text.replace('&lsquo;', '')
        text = text.replace('&middot;', '')
        text = text.replace('&rsquo;', '')
        text = text.replace('\n', '')
        text = text.replace('\t', '')
        # print(text)

        lib_dic['id'].append(id)
        lib_dic['content'].append(text)


    except:
        time.sleep(2)

pd.DataFrame(lib_dic).to_csv(BASE_DIR / 'crawling_library_notice_content.csv', encoding='utf-8-sig', index=False)

print('crawling_library_notice_content.csv done!')
