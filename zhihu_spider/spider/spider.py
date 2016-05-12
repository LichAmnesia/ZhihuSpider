#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
import requests
import logging
import random
import urllib.request
import urllib.parse
import urllib.error
import time
import os,sys


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, BASE_DIR)


from db import Account
from db import AccountDAO
from db import RawDataDAO
from db import AnswerDAO
from db import QuestionDAO
# 
# from .parser import Parser
# from .tweetp import TweetP
# from .captcha import CaptchaDecoderFactory
import settings

class LoginFailedException(Exception):
    pass


class Spider(object):

    def __init__(self, account, rawdata_dao=None, answer_dao=None, question_dao=None):
        """
        爬虫类， 每个使用一个账户.

        account: Account 对象
        rawdata_dao: RawDataDAO
        answer_dao: AnswerDAO
        """
        assert isinstance(account, Account)
        if rawdata_dao:
            if rawdata_dao is True:
                rawdata_dao = RawDataDAO()
            assert(isinstance(rawdata_dao, RawDataDAO))
        if answer_dao:
            if answer_dao is True:
                answer_dao = AnswerDAO()
            assert(isinstance(answer_dao, AnswerDAO))
        if question_dao:
            if question_dao is True:
                question_dao = QuestionDAO()
            assert(isinstance(question_dao, QuestionDAO))
        self.account = account
        self.rawdata_dao = rawdata_dao
        self.answer_dao = answer_dao
        self.question_dao = question_dao
        self.s = requests.session()
        # 设置cookie
        self.set_session_cookie(session=self.s,
                                cookies=account.cookies)
        self.s.headers['User-Agent'] = settings.HEADERS['User-Agent']
        self.referer = ''
        # 待修改
        # self.parser = Parser()
        self.fetch('http://zhihu.com')
        # self.capthca_decoder = CaptchaDecoderFactory('Ruokuai')()

    def __del__(self):
        self.save_cookies()
        logging.info('Destory spider {email}.'.format(email=self.account.email))

    def __repr__(self):
        return "<Spider: %s>" % self.account.email

    @classmethod
    def set_session_cookie(cls, session, cookies):
        cookies = json.loads(cookies)
        for cookie in cookies:
            # domain expiry httpOnly name path secure
            # print(session.cookies)
            session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                path=cookie['path'],
                # httpOnly=cookie['httpOnly'],
                domain=cookie['domain'],
                expires=cookie.get('expires') or cookie.get('expiry')
            )
        # print(cookies)

    @classmethod
    def get_session_cookies(cls, session):
        cookies = []
        for cookie in session.cookies:
            cookies.append(dict(
                name=cookie.name,
                value=cookie.value,
                path=cookie.path,
                # httpOnly=cookie.httpOnly,
                domain=cookie.domain,
                expires=cookie.expires
            ))
        return cookies

    def save_cookies(slef):
        slef.account.cookies = json.dumps(slef.get_session_cookies(slef.s))
        account_dao = AccountDAO()
        account_dao.commit()

    def handle_login_failed(self):
        self.account.is_login = False
        account_dao = AccountDAO()
        account_dao.commit()
        raise LoginFailedException

    @classmethod
    def check_relogin(cls, resp):
        """
        检查是否是重新登陆页面
        """

        cond1 = re.search(r'SignupForm', resp.text)
        # cond2 = re.search(r'var restore_back = function \(response\)', resp.text)
        return cond1 is not None
         # and cond2 is not None

    def fetch(self, url, referer=None):
        """
        抓取一个页面，处理各种需要的跳转和重登录
        """
        if referer is None:
            referer = self.referer
        self.s.headers['Referer'] = referer
        resp = self.s.get(url=url)

        # 检测是不是出问题无法获得网页
        while True:
            if self.check_relogin(resp):
                logging.info("Fetching encounter relogin:\n")
                print("Fetching encounter relogin")
                self.handle_login_failed()
                continue
            break
        print("Fetching success!!")
        self.referer = resp.url
        self.last_resp = resp
        return resp


def get_random_spider():
    account_dao = AccountDAO()
    account = account_dao.get_random_account()
    rawdata_dao = RawDataDAO()
    answer_dao = AnswerDAO()
    spider = Spider(account=account, rawdata_dao=rawdata_dao, answer_dao=answer_dao)
    return spider


if __name__ == '__main__':
    get_random_spider()
