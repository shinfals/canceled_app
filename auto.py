# -*- coding: utf-8 -*-
import time
import requests
import pandas as pd
import csv
import os.path
import re
import numpy as np
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def start_chrome():
    # chromedriverのPATHを指定（Pythonファイルと同じフォルダの場合）
    driver_path = '../chromedriver'

    options = Options()
    #chromeの場所指定
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options, executable_path=driver_path)

    # GoogleログインURL
    url = 'https://service.cloud.teu.ac.jp/inside2/hachiouji/hachioji_common/cancel/'
    driver.get(url)

    return driver

def login_google(driver):
    #ログイン情報
    login_id = "c011701087@edu.teu.ac.jp"
    login_pw = "@m67KWrcv"

    #最大待機時間（秒）
    wait_time = 30

    ### IDを入力
    login_id_xpath = '//*[@id="identifierNext"]'
    # xpathの要素が見つかるまで待機します。
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, login_id_xpath)))
    driver.find_element_by_name("identifier").send_keys(login_id)
    driver.find_element_by_xpath(login_id_xpath).click()


    time.sleep(3)
    ### パスワードを入力
    login_pw_xpath = '//*[@id="passwordNext"]'
    # xpathの要素が見つかるまで待機します。
    WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, login_pw_xpath)))
    driver.find_element_by_name("password").send_keys(login_pw)
    time.sleep(1) # クリックされずに処理が終わるのを防ぐために追加。
    driver.find_element_by_xpath(login_pw_xpath).click()

    time.sleep(1)

    ###休講情報テーブル取得&csv保存
    cancel_new = []
    #page指定するための番号
    num = 1
    #現在のurlを取得
    url = driver.current_url
    while True:
        #urlを使用できるように置き換え&そのurlを開く
        new_url = re.sub("https://service.cloud.teu.ac.jp/inside2/hachiouji/hachioji_common/cancel/", "https://service.cloud.teu.ac.jp/inside2/hachiouji/hachioji_common/cancel/page/"+str(num)+"/", url)
        driver.get(new_url)
        c_name = driver.find_elements_by_class_name("searchTable")
        #searchTableクラスを持つ要素がある場合のみ処理を続行
        if  len(c_name) != 0:
            dfs = pd.read_html(new_url)
            for i in range(0, len(dfs)):
                dfs[i][1].to_csv("./canceled_info_new.csv", mode='a', header=True, index=False)
                i += 1
            num += 1
        else:
            break

    read_and_compare_csv(cancel_new)
    os.remove("./canceled_info_old.csv")
    os.rename("./canceled_info_new.csv", "./canceled_info_old.csv")


###csvから旧休講情報と新休講情報を読み込み比較する
def read_and_compare_csv(cancel_new):
    line_nl = [0]*5
    count = 0

    df_old = pd.read_csv("./canceled_info_old.csv", names=('a'))
    df_new = pd.read_csv("./canceled_info_new.csv", names=('a'))

    df_diff = df_new[~df_new['a'].isin(df_old['a'])]
    line = df_diff.values.tolist()

    for i in range(int(len(line)/5)):
        for j in range(0, 5):
            if i == 0:
                line_nl[j] = list('\n')+line[j]
            else:
                line_nl[j] = list('\n')+line[j+count_plus]
            count += 1
        count_plus = count
        line_notify(line_nl)

def line_notify(message):
    url = "https://notify-api.line.me/api/notify"
    token = "v2lifN1LeDV2zdRwOnepLyHkTVQYXmcUTKtezQy98ZC"
    headers = {"Authorization" : "Bearer "+ token}

    payload = {"message" :  message}
    requests.post(url ,headers = headers ,params=payload)

if __name__ == '__main__':
    # Chromeを起動
    driver = start_chrome()

    # Googleにログイン
    login_google(driver)
