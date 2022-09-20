import time
import urllib
from pathlib import Path
import scrapy
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By  # selenium 상위 버전(4)
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent

# selenum의 webdriver에 앞서 설치한 chromedirver를 연동한다.
driver = webdriver.Chrome(ChromeDriverManager().install())

df_dic = {'content': []}  # 공지사항 각각으로 들어갔을때의 내용데이터
title_dic = {'title': [], 'date': []}  # 공지사항 외부의 제목, 게시일자 데이터
test = []

for p in range(10):  # page num
    num = p * 20
    base_url = 'https://discover.duksung.ac.kr/#/bbs/notice'
    page = f'?offset={num}&max=20'
    url = base_url + page
    # driver로 특정 페이지를 크롤링한다.
    driver.get(url)

    # 웹 페이지가 열릴 때 까지 기다림
    driver.implicitly_wait(3)
    time.sleep(3)


    def get_data(tr):
        trs = tr
        for i in trs:
            post_date = ((i.text.split())[::-1])[0]

            for k in i.text.split():
                if k != post_date and k != i.text.split()[0]:
                    test.append(k)  # ['[공지]', '덕성여대', '도서관', '모바일학생증', '발급', '이용', '방법']
                title = " ".join(test)
            title_dic['title'].append(title)
            title_dic['date'].append(post_date)
            test.clear()


    if p == 0:  # first page is different table tag
        tbody = driver.find_element(By.CSS_SELECTOR,
                                    "#goto-content > div > div > div > div:nth-child(5) > table > tbody:nth-child(3)")
        trs = tbody.find_elements(By.CSS_SELECTOR, "tr")

        get_data(trs)

        second_tbody = driver.find_element(By.CSS_SELECTOR,
                                           '#goto-content > div > div > div > div:nth-child(5) > table > tbody:nth-child(4)')
        second_trs = second_tbody.find_elements(By.CSS_SELECTOR, "tr")

        get_data(second_trs)
    else:
        tbody = driver.find_element(By.CSS_SELECTOR,
                                    "#goto-content > div > div > div > div:nth-child(5) > table > tbody:nth-child(3)")
        trs = tbody.find_elements(By.CSS_SELECTOR, "tr")
        get_data(trs)
        # print(f'title_dic: {title_dic}')
        #
        # driver.find_element(By.CSS_SELECTOR,
        #                     '#goto-content > div > div > div > div:nth-child(5) > table > tbody:nth-child(3) > tr:nth-child(1) > td.ikc-contents > span:nth-child(2) > span > a').click()
        # time.sleep(0.5)
        # driver.implicitly_wait(3)
        # # 페이지 내용
        # content = driver.find_element(By.XPATH,'/html/body') # 에러 발생 # 왜 요소가 안보일까
        # print(content.text)
        # # 앵귤러 기반이라 그런듯 한데, #document안에 있는 본문 내용만 안보임
        # # 모바일학생증_발급_이용_안내.pdf 220KB 라는 파일 이름도 가져와짐.
        #
        # #naeyong= content.text
        #
        #
        #
        # # 이미지 크롤링
        # imgs = driver.find_element(By.CSS_SELECTOR,'body > p > img')
        # img_url=[]
        #
        # for img in imgs:
        #     url = img.get_attribute('src')
        #     img_url.append(url)
        # # 이미지 저장
        # import os
        # img_folder = BASE_DIR + '/img'
        # if not os.path.exists(img_folder):
        #     os.makedirs(img_folder)
        # for index, link in enumerate(img_url):
        #     urllib.request.urlretrieve(link, f'{img_folder}/{index}.jpg')

        # data frame으로 저장

    time.sleep(1)
    driver.back()  # 들여쓰기 주의
    time.sleep(10)

pd.DataFrame(title_dic).to_csv(BASE_DIR / 'crawling_library_notice_title.csv', encoding='utf-8-sig')
print('crawling_library_notice_title.csv done!')
