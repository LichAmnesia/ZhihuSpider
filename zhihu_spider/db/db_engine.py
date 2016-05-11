# -*- coding: utf-8 -*-
# @Author: Lich_Amnesia
# @Email: alwaysxiaop@gmail.com
# @Date:   2016-05-11 14:04:06
# @Last Modified time: 2016-05-11 15:17:53
# @FileName: db_engine.py
# db的创建，db对象访问为单例模式
# 需要在mysql里面创建好数据库，并且字符模式为utf8mb4

# import os
# import sys

from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, BASE_DIR)

from core import Singleton
import settings

# 创建对象的基类:
Base = declarative_base()


class DBEngine(Singleton):

    def __init__(self):
        self.connect_string = 'mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4'.format(
            **settings.MYSQL_SETTINGS)
        print(self.connect_string)
        __engine = create_engine(self.connect_string, echo=False)
        self.engine = __engine.connect()
        # 建立数据库连接
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_db(self):
            """建立数据库.Base.metadata.create_all(engine) 会找到 Base 的所有子类，并在数据库中建立这些表"""
            Base.metadata.create_all(self.engine)

if __name__ == '__main__':

    import IPython

    IPython.embed()
