# -*- coding: utf-8 -*-
# @Author: Lich_Amnesia
# @Email: alwaysxiaop@gmail.com
# @Date:   2016-05-12 10:46:37
# @Last Modified time: 2016-05-13 12:58:01
# @FileName: question.py


"""question数据库存储"""
from sqlalchemy import Column, Integer, String, TEXT, DATETIME, Boolean
from sqlalchemy.sql.expression import func

from .db_engine import Base
from .db_engine import DBEngine

from core import Singleton


class Question(Base):
    """
    表示一条问题.

    id: 主键
    is_fetch: 是否已抓取
    questionid: 问题id
    questionurl: /question/37093377
    title: 标题
    detail: 详细解释
    topics: 所属话题
    comment: 评论数
    answernum: 回答数
    fetch_timestamp: 抓取时间戳
    """
    __tablename__ = 'question'

    id = Column(Integer, primary_key=True)
    is_fetch = Column(Boolean, default=False)
    questionid = Column(String(50))
    questionurl = Column(String(100), unique=True)
    title = Column(String(200))
    detail = Column(TEXT)
    topics = Column(String(500))
    comment = Column(Integer)
    answernum = Column(Integer)
    fetch_timestamp = Column(DATETIME)

    def __repr__(self):
        """__repr__."""
        return "<Questionid: {0}>,<Title: {1}>".format(self.questionid, self.title)

class QuestionDAO(Singleton):

    def __init__(self):
        self.engine = DBEngine()
        self.session = self.engine.session

    def save_question(self, one_question):
        if not one_question['questionid']:
            return None
        question = Question(
            is_fetch=one_question['is_fetch'],
            questionid=one_question['questionid'],
            questionurl=one_question['questionurl'],
            title=one_question['title'],
            detail=one_question['detail'],
            topics=one_question['topics'],
            comment=one_question['comment'],
            answernum=one_question['answernum'],
            fetch_timestamp=one_question['fetch_timestamp'],
        )
        self.session.add(question)
        self.session.commit()
        return question

    def update_or_create_question(self, one_question):
        created = False
        if not one_question['questionid']:
            return created, None
        question = self.session.query(Question).filter(
            Question.questionurl == one_question['questionurl'] and Question.is_fetch == true()).one_or_none()
        # 如果是 is_fetch 就不进行下去
        if question:
            question = self.session.query(Question).filter(
            Question.questionurl == one_question['questionurl'] and Question.is_fetch == true()).first()
            created = True
            return created, question
        # 未抓取或者没信息
        question = self.session.query(Question).filter(
            Question.questionurl == one_question['questionurl'] and Question.is_fetch == false()).one_or_none()
        if question:
            question.is_fetch = one_question['is_fetch'],
            question.title = one_question['title']
            question.detail = one_question['detail']
            question.topics = one_question['topics']
            question.comment = one_question['comment']
            question.answernum = one_question['answernum']
            question.fetch_timestamp = one_question['fetch_timestamp']
            self.session.commit()
        else:
            question = self.save_question(one_question)
            created = True

        return created, question

    def get_random_question(self):
        q = self.session.query(Question).filter(Question.is_fetch == False and Question.answernum >= 5).order_by(func.rand()).limit(10)
        print(q.first())
        return q.first()
