# -*- coding: utf-8 -*-
# @Author: Lich_Amnesia
# @Email: alwaysxiaop@gmail.com
# @Date:   2016-05-11 22:39:06
# @Last Modified time: 2016-05-13 11:55:52
# @FileName: gettopics.py



import _thread
import time
import logging
import datetime
from .spider import Spider
# from db.wordfollow import WordFollowDAO
from db import Account
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
    def __init__(self, topicsurl, account=None):
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
        self.get_topics_questions()
        # self.start()

    def get_nofetch_question(self):
        pass

    def get_all_answers(self):
        pass

    # 就获取topics下所有问题
    # /topic/19805970/questions?page=
    def get_topics_questions(self):
        for id in range(1517, 6966):
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
                time.sleep(random.randint(10,20))
            elif rand_num % 10 == 0:
                time.sleep(random.randint(5,10))

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
                        'is_fetch':False,
                        'questionid':question_id,
                        'questionurl':question_url,
                        'answernum':question_answerCount,
                        'title':question_title,
                        'detail':None,
                        'topics':None,
                        'comment':None,
                        'fetch_timestamp':datetime.datetime.now(),
                    }
                    if self.spider.question_dao:
                        self.spider.question_dao.update_or_create_question(one)
                        # file.write((str(question_url)+'\n').encode())
                        # cli.proid.insert_one({'_id': question_id, 'question_title':question_title, 'question_url':question_url})
            nodeId += 1
        print("增加问题: {0}".format(add_question))
        return 0



    def start(self):
        _thread.start_new_thread(self.worker, ())

    def worker(self):
        while self.soup is None:
            it = self.spider.fetch(url=self.url)
            soup = BeautifulSoup(it.content)
            self.soup = soup
        self.oneanswer.uid, self.oneanswer.username = self.get_author()
        self.oneanswer.like = self.get_like()
        self.oneanswer.questionid = self.url.split('/')[4]
        self.oneanswer.answerid = self.url.split('/')[-1]
        self.oneanswer.answerurl = self.url
        self.oneanswer.comment = self.get_comment()
        self.oneanswer.content = self.to_md(self.get_content())
        print(self.oneanswer)
        self.save_oneanswer(self.oneanswer)

    def to_md(self, content):
        text = html2text.html2text(content.decode('utf-8')).encode("utf-8")
        return text

    # 获取回答内容
    def get_content(self):
        soup = BeautifulSoup(self.soup.encode("utf-8"))
        answer = soup.find("div", class_="zm-editable-content clearfix")
        soup.body.extract()
        soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))
        soup.body.append(answer)
        img_list = soup.find_all("img", class_="content_image lazy")
        for img in img_list:
            img["src"] = img["data-actualsrc"]
        img_list = soup.find_all("img", class_="origin_image zh-lightbox-thumb lazy")
        for img in img_list:
            img["src"] = img["data-actualsrc"]
        noscript_list = soup.find_all("noscript")
        for noscript in noscript_list:
            noscript.extract()
        content = soup
        return content

    # 获取评论数目
    def get_comment(self):
        soup = self.soup
        comment = soup.find("a", class_="meta-item toggle-comment js-toggleCommentBox").get_text(strip='\n').split(' ')[0]
        return comment

    def get_author(self):
        soup = self.soup
        if soup.find("div", class_="zm-item-answer-author-info").get_text(strip='\n') == u"匿名用户":
            # username_url = None
            uid = "anonymous_users"
            username = "匿名用户"
        else:
            username_tag = soup.find("div", class_="zm-item-answer-author-info").find_all("a")[1]
            username = username_tag.string
            # username_url = "http://www.zhihu.com" + username_tag["href"]
            uid = username_tag["href"].split('/')[-1]
            # author = User(author_url, author_id)
        return uid, username

    def get_like(self):
        if hasattr(self, "like"):
            return self.oneanswer.like
        else:
            soup = self.soup
            count = soup.find("span", class_="count").string
            if count[-1] == "K":
                like = int(count[0:(len(count) - 1)]) * 1000
            elif count[-1] == "W":
                like = int(count[0:(len(count) - 1)]) * 10000
            else:
                like = int(count)
            return like



    def save_oneanswer(self, oneanswer):
        one = {
            'uid': self.oneanswer.uid,
            'username': self.oneanswer.username,
            'like': self.oneanswer.like,
            'questionid': self.oneanswer.questionid,
            'answerid': self.oneanswer.answerid,
            'answerurl':self.oneanswer.answerurl,
            'comment':self.oneanswer.comment,
            'content':self.oneanswer.content,
            'timestamp':self.oneanswer.timestamp,
            'fetch_timestamp':self.oneanswer.fetch_timestamp,
        }
        print(one)
        if self.spider.answer_dao:
            self.spider.answer_dao.update_or_create_answer(one)

    def __update(self):
        it = self.spider.fetch_search_iter(keyword=self.wordfollow.word)
        newest_ts = self.wordfollow.newest_timestamp
        min_ts = int((time.time() + 3600) * 1000)
        max_ts = 0
        num_new = 0
        logging.info('start __update loop.')
        for weibos, page, _ in it:
            logging.info('__update page {0}.'.format(page))
            for weibo in weibos:
                if weibo.timestamp >= newest_ts:  # New
                    print(weibo.pretty())
                    num_new += 1
                max_ts = max(max_ts, weibo.timestamp)
                min_ts = min(min_ts, weibo.timestamp)
            logging.info("min_ts={min_ts}, max_ts={max_ts}, newest_ts={newest_ts}.".format(
                min_ts=min_ts, max_ts=max_ts, newest_ts=newest_ts))
            if min_ts < newest_ts:
                logging.info('break __update.')
                break
            # if page % 10 == 0:
            #     time.sleep(10)
        self.wordfollow.newest_timestamp = max(self.wordfollow.newest_timestamp, max_ts)
        self.wordfollow_dao.commit()
        return num_new

    def follow_worker(self):
        while self.running:
            num_new = self.__update()
            fetch_interval = self.fetch_interval
            if num_new > 30:
                fetch_interval *= 0.618
            elif num_new < 10:
                fetch_interval *= 1.618
            fetch_interval = min(300, max(20, fetch_interval))
            self.fetch_interval = int(fetch_interval)
            word = self.wordfollow.word
            logging.info('WordFollower {0} got {1} new, and going to sleep {2} seconds.'.format(
                word, num_new, self.fetch_interval))
            time.sleep(self.fetch_interval)

if __name__ == '__main__':
    a = GetAnswer("/question/21923064/answer/19797280")
