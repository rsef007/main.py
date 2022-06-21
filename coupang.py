# 크롬 드라이버 위치 확인
# import os
# print(os.getcwd())

# db import
from sqlalchemy import create_engine
import pandas as pd

# main import

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# create num
import string
import random

class coupang:
    def __init__(self, url):
        # db con
        self.db_host = 'localhost'
        self.db_user = 'root'
        self.db_id = 'test'
        self.db_pw = 'abcd1234'
        self.db_port = '3306'
        self.db_insert = False

        # page_info
        self.page_url = url

        # create_num
        self.numbering = 8

        # page_num
        self.page_num = 10

        # set
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome('D:\project\Web_Crawling\chromedriver.exe', chrome_options=self.options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument",
                               {"source": """ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) """})


    def create_num(self):
        string_pool = string.digits

        result = ""
        for i in range(self.numbering):
            result += random.choice(string_pool)
        return result


    def page_all_num(self):
        driver = self.driver
        list = []

        id = driver.find_element(by=By.ID, value='product-list-paging')
        num = id.find_elements(by=By.TAG_NAME, value='a')

        for i in num:
            data = i.get_attribute('data-page')
            list.append(data)

        page_num = list[1:-1]

        return page_num


    def page_now_num(self):
        driver = self.driver
        list = []

        id = driver.find_element(by=By.ID, value='product-list-paging')
        num2 = id.find_elements(by=By.CLASS_NAME, value='selected')

        for i in num2:
            data = i.get_attribute('data-page')
            list.append(data)

        return list[0]


    def croawling(self):
        driver = self.driver

        # 크롬 드라이버 url 지정
        driver.get(self.page_url)
        print(self.page_url)

        print('로켓배송 클릭')
        driver.find_element(by=By.XPATH, value='//*[@id="header"]/section/ul/li[1]/a').click()
        time.sleep(2)

        print('가전디지털 클릭')
        driver.find_element(by=By.XPATH, value='//*[@id="searchOptionForm"]/div/div/div[1]/div[3]/div[5]/a/div[1]/img').click()
        time.sleep(2)

        page_all_num = coupang.page_all_num(self)
        page_now_num = coupang.page_now_num(self)

        coupang_id = []
        coupang_nm = []
        coupang_sale = []
        coupang_oj_price = []
        coupang_price = []

        print('크롤링 시작')
        nm = driver.find_elements(by=By.CSS_SELECTOR,value='.name')
        sale = driver.find_elements(by=By.CSS_SELECTOR, value='.discount-percentage')
        oj_price = driver.find_elements(by=By.CSS_SELECTOR, value='.base-price')
        price = driver.find_elements(by=By.CSS_SELECTOR, value='.price-value')

        for i in range(len(nm)):
            coupang_id.append(coupang.create_num(self))
            coupang_nm.append(nm[i].text)
            try:
                coupang_sale.append(sale[i].text)
                coupang_oj_price.append(oj_price[i].text)
            except:
                coupang_sale.append('')
                coupang_oj_price.append('')

            coupang_price.append(price[i].text)

        coupang_data = pd.DataFrame((zip(coupang_id, coupang_nm, coupang_sale, coupang_oj_price, coupang_price))
                                    , columns=['id','nm','sale','oj_price','price'])
        print(coupang_data)

        if self.db_insert == True:
            coupang.db_insert(self, coupang_data)

        time.sleep(5)


    def db_insert(self, coupang_data):
        try:

            db_connection_str = f'mysql+pymysql://{self.db_user}:{self.db_pw}@{self.db_host}/{self.db_id}'
            db_connection = create_engine(db_connection_str)

            coupang_data.to_sql(name='coupang', con=db_connection, if_exists='append', index=False)
            print('commit')

        except Exception as e:
            print(e)