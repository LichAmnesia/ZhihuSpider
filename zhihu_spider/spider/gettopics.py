# -*- coding: utf-8 -*-
# @Author: Lich_Amnesia
# @Email: alwaysxiaop@gmail.com
# @Date:   2016-05-11 22:39:06
# @Last Modified time: 2016-05-13 20:37:22
# @FileName: gettopics.py

# import _thread
import time
# import logging
import datetime
from .spider import Spider
# from db.wordfollow import WordFollowDAO
# from db import Account
from db import AccountDAO
from db import RawDataDAO
from db import AnswerDAO
from db import QuestionDAO
from bs4 import BeautifulSoup
import html2text
from lxml import etree
from lxml.html import document_fromstring
import random

import settings


class GetTopics(object):
    """获得一个话题下所有问题的类封装."""

    # /topic/19805970/questions?page=
    def __init__(self, topicsurl, begin=1, end=1, account=None):
        # self.wordfollow_dao = WordFollowDAO()
        # self.wordfollow = self.wordfollow_dao.get_or_create(word=word)
        self.url = settings.URL['base_url'] + topicsurl
        if not account:
            account_dao = AccountDAO()
            account = account_dao.get_random_account()
        print(account)
        self.account = account
        self.spider = Spider(account=self.account, rawdata_dao=True, answer_dao=True, question_dao=True)
        self.soup = None
        # self.oneanswer = OneAnswer()
        self.get_topics_questions(begin, end)
        # self.start()

    def get_nofetch_question(self):
        pass

    def get_all_answers(self):
        pass

    # 就获取topics下所有问题
    # /topic/19805970/questions?page=
    def get_topics_questions(self, begin=1, end=1):
        for id in range(begin, end):
            questionpage_id = str(id)
            # it = self.spider.fetch(url=self.url)
            # soup = BeautifulSoup(it.content)
            # import IPython
            # IPython.embed()
            while True:
                it = self.spider.fetch(self.url + questionpage_id)
                if it.status_code != 200:
                    print("wait for 5 seconds")
                    time.sleep(5)
                    continue
                break

            print(self.url + questionpage_id)
            self._parse_json(it.text)
            rand_num = random.randint(50, 1000)
            if rand_num % 7 == 0:
                time.sleep(random.randint(10, 20))
            elif rand_num % 10 == 0:
                time.sleep(random.randint(5, 10))

    # 得到本页面的问题url
    def _parse_json(self, string):
        # res_json = json.loads(string,'utf-8')['msg']
        try:
            html = document_fromstring(string)
        except Exception as e:
            # log_main.error(e)
            sys.exit(-1)
        # 获得问题答案数目
        answerCount = html.xpath(u"//meta[@itemprop='answerCount']")
        ansList = []
        for ans in answerCount:
            ansList.append(int(ans.attrib['content']))

        # nodeId 表示页面中的第几个问题
        nodeId = 0
        # 增加的问题数目
        add_question = 0
        nodes = html.xpath(u"//a[@class='question_link']")

        for node in nodes:
            # logitem_id = int(node.xpath('@id')[0].split('-')[-1])

            question_title = node.text
            question_url = node.attrib['href']
            # question_url = settings.URL['base_url'] + question_url

            question_id = node.attrib['href'].split('/')[2]
            question_answerCount = ansList[nodeId]
            if question_answerCount >= 1:
                if question_title.strip() != '' and question_url.strip() != '' and question_id.strip() != '':
                    add_question += 1
                    one = {
                        'is_fetch': False,
                        'questionid': question_id,
                        'questionurl': question_url,
                        'answernum': question_answerCount,
                        'title': question_title,
                        'detail': None,
                        'topics': None,
                        'comment': None,
                        'fetch_timestamp': datetime.datetime.now(),
                    }
                    if self.spider.question_dao:
                        self.spider.question_dao.update_or_create_question(one)
                        # file.write((str(question_url)+'\n').encode())
                        # cli.proid.insert_one({'_id': question_id, 'question_title':question_title, 'question_url':question_url})
            nodeId += 1
        print("增加问题: {0}".format(add_question))
        return 0


