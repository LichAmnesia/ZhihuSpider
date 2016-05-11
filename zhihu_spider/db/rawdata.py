# -*- coding: utf-8 -*-
# @Author: Comzyh
# @Date:   2016-04-20 01:51:12
# @Last Modified by:   Comzyh
# @Last Modified time: 2016-04-20 01:52:08

import settings

from core import Singleton


class RawDataDAO(Singleton):
    """提供微博原始数据的存储和查询"""
    def __init__(self):
        import plyvel
        self.db = plyvel.DB(settings.RAW_DATA_STORGE['path'], create_if_missing=True)

    def set_raw_data(self, mid, data, replace=False):
        if isinstance(mid, str):
            mid = mid.encode('utf-8')
        if isinstance(data, str):
            data = data.encode('utf-8')
        if not replace and self.db.get(mid):
            return
        self.db.put(mid, data)

    def get_raw_data(self, mid):
        if isinstance(mid, str):
            mid = mid.encode('utf-8')
        assert(isinstance(mid, str))
        return self.db.get(mid)
