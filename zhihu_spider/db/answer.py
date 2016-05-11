# -*- coding: utf-8 -*-
# @Author: Lich_Amnesia
# @Email: alwaysxiaop@gmail.com
# @Date:   2016-05-11 20:30:37
# @Last Modified time: 2016-05-12 00:48:30
# @FileName: answer.py


"""answer数据库存储"""
from sqlalchemy import Column, Integer, String, TEXT, DATETIME

from .db_engine import Base
from .db_engine import DBEngine

from core import Singleton


class Answer(Base):
    """
    表示一条回答.

    id: 主键
    uid: 作者id
    username: 作者昵称
    questionid: 问题id
    answerid: 回答id
    answerurl:
    content: 内容
    comment: 评论数
    like: 赞数
    fetch_timestamp: 抓取时间戳
    timestamp: 时间戳
    """
    __tablename__ = 'answer'

    id = Column(Integer, primary_key=True)
    uid = Column(String(50))
    username = Column(String(50))
    questionid = Column(String(50))
    answerid = Column(String(50))
    answerurl = Column(String(60), unique=True)
    content = Column(TEXT)
    comment = Column(Integer)
    like = Column(Integer)
    fetch_timestamp = Column(DATETIME)
    timestamp = Column(DATETIME)


class AnswerDAO(Singleton):

    def __init__(self):
        self.engine = DBEngine()
        self.session = self.engine.session

    def save_answer(self, one_answer):
        if not one_answer.answerid:
            return None
        answer = Answer(
            uid=one_answer.uid,
            username=one_answer.username,
            questionid=one_answer.questionid,
            answerid=one_answer.answerid,
            answerurl=one_answer.answerurl,
            content=one_answer.content,
            comment=one_answer.comment,
            like=one_answer.like,
            fetch_timestamp=one_answer,
            timestamp=one_answer.timestamp,
        )
        self.session.add(answer)
        self.session.commit()
        return answer

    def update_or_create_answer(self, one_answer):
        created = False
        if not one_answer.answerid:
            return created, None
        answer = self.session.query(Answer).filter(
            Answer.answerurl == one_answer.answerurl).one_or_none()
        if answer:
            answer.uid = one_answer['uid']
            answer.username = one_answer['username']
            answer.content = one_answer['content']
            answer.comment = one_answer['comment']
            answer.like = one_answer['like']
            answer.fetch_timestamp = one_answer['fetch_timestamp']
            answer.timestamp = one_answer['timestamp']
            self.session.commit()
        else:
            answer = self.save_answer(one_answer)
            created = True

        return created, answer

