import os
from fake_useragent import UserAgent
from selenium import webdriver
import io
import time
import datetime
from datetime import datetime as dt
import pandas as pd
from bs4 import BeautifulSoup
import pytz
import lxml

USER_ID = "あなたのID"
USER_PW = "あなたのパスワード"

def handler(request):
   chrome_options = webdriver.ChromeOptions()

   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--disable-gpu')
   chrome_options.add_argument('--window-size=1280x1696')
   chrome_options.add_argument('--no-sandbox')
   chrome_options.add_argument('--hide-scrollbars')
   chrome_options.add_argument('--enable-logging')
   chrome_options.add_argument('--log-level=0')
   chrome_options.add_argument('--v=99')
   chrome_options.add_argument('--single-process')
   chrome_options.add_argument('--ignore-certificate-errors')
   chrome_options.add_argument('user-agent='+UserAgent().random)

   chrome_options.binary_location = os.getcwd() + "/headless-chromium"    
   driver = webdriver.Chrome(os.getcwd() + "/chromedriver",chrome_options=chrome_options)

   # SBI証券のサイトにログイン
   login_sbisec(USER_ID,USER_PW,driver)

def login_sbisec(USER_ID,USER_PW,driver):

   # 待機時間を10秒に設定
   driver.implicitly_wait(10)
   
   # SBI証券のトップ画面を開く
   driver.get('https://www.sbisec.co.jp/ETGate')
   
   # ユーザーIDとパスワードをセット
   driver.find_element_by_name('user_id').send_keys(USER_ID)
   driver.find_element_by_name('user_password').send_keys(USER_PW)
   
   # ログインボタンをクリックしてログイン
   driver.find_element_by_name('ACT_login').click()

   # テスト
   print(driver.page_source)