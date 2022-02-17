# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: config.py
@time: 2022/1/7 15:11
"""


import json


class GetConfig():
    # 加载配置文件
    def parse_account(file):
        with open(file, 'r', encoding='utf-8') as f:
            conf_data = json.load(f)
        return conf_data

    # 读取配置账户里的值并赋值返回
    def access(item):
        name = item[0]
        region_id = item[1]
        access_key_id = item[2]
        access_key_secret = item[3]

        # print(access_key_id, access_key_secret, regionId)
        return access_key_id, access_key_secret, name, region_id
