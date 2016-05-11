# -*- coding: utf-8 -*-
# @Author: Lich_Amnesia
# @Email: alwaysxiaop@gmail.com
# @Date:   2016-05-11 14:04:07
# @Last Modified time: 2016-05-11 22:55:35
# @FileName: manul_login.py
# 登录知乎程序

import datetime
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import time

import settings
from db import AccountDAO


class LoginExecuter(object):
    """docstring for LoginExecuter"""

    def __init__(self):
        super(LoginExecuter, self).__init__()
        self.browser = webdriver.Chrome()

    def login(self, username, password):
        # 整体操作太容易出错了
        # print(username, password)
        try:
            self.browser.delete_all_cookies()
            self.browser.get(settings.URL['login_url'])
            # 按照XPATH格式，检索class，如果找到认为网页加载完毕，这个classname只能检索一个变量
            normal_tab = WebDriverWait(self.browser, 10).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "email")))
            normal_tab.click()  # 点击'账号登陆'
            username_input = WebDriverWait(self.browser, 1).until(
                expected_conditions.presence_of_element_located((By.NAME, "account")))
            # username_input = self.browser.find_element_by_name('username')
            password_input = WebDriverWait(self.browser, 1).until(
                expected_conditions.presence_of_element_located((By.NAME, "password")))
            submit_btn = self.browser.find_element_by_xpath(
                "//button[@type='submit']")
            username_input.clear()
            username_input.send_keys(username)
            # 防止出现填写太快的情况
            time.sleep(3)
            password_input.clear()
            password_input.send_keys(password)
            try:
                submit_btn.click()
            except Exception:
                pass

            # 检测登陆成功
            normal_tab = WebDriverWait(self.browser, 40).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, "zu-top-nav-userinfo")))
            print('login successful')

            cookies = self.browser.get_cookies()
            # self.browser.get("http://passport.weibo.com/js/visitor/mini.js")
            print(cookies)
            nickname = WebDriverWait(self.browser, 1).until(
                expected_conditions.presence_of_element_located((By.XPATH, "//span[@class='name']"))).text
            print(nickname)
            print('login successful')
            # self.browser.get("https://passport.weibo.com/visitor/")
            # for cookie in self.browser.get_cookies():
            #     print(cookie['domain'])
            #     if cookie['domain'].find('passport.weibo.com') != -1:
            #         cookies.append(cookie)
        except Exception:
            logging.exception('Login failed')
            return None
        else:
            return cookies, nickname


def import_account_from_file(filename):
    account_file = open(filename, 'r')
    line_num = 0
    create_num = 0
    account_dao = AccountDAO()
    for line in account_file.readlines():
        print (line)
        line_num += 1
        line = line.strip('\n')
        email, password = line.split('----')[:2]
        _, created = account_dao.update_or_create(email=email, password=password)
        if created:
            create_num += 1
    print('{line} lines, {created} created.'.format(line=line_num, created=create_num))


def login(login_executer, email, password):
    resp, nickname = login_executer.login(email, password)
    if not resp:
        return False
    account_dao = AccountDAO()
    account_dao.update_or_create(email=email,
                                 password=password,
                                 name=nickname,
                                 is_login=True,
                                 login_time=datetime.datetime.now(),
                                 cookies=json.dumps(resp))
    return True


def start_login():
    login_executer = LoginExecuter()
    for account in AccountDAO().not_login_iter():
        # print(account.email, account.password)
        login(login_executer=login_executer, email=account.email, password=account.password)
        time.sleep(2)
    print("Login successful!!")
