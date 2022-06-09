# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: config.py
@time: 2022/1/7 15:11
"""
# import json
#
#
# class GetConfig():
#     # 加载配置文件
#     def parse_account(file):
#         with open(file, 'r', encoding='utf-8') as f:
#             conf_data = json.load(f)
#         return conf_data
#
#     # 读取配置账户里的值并赋值返回
#     def access(item):
#         name = item[0]
#         region_id = item[1]
#         access_key_id = item[2]
#         access_key_secret = item[3]
#
#         # print(access_key_id, access_key_secret, regionId)
#         return access_key_id, access_key_secret, name, region_id


import yaml


class GetConfig(object):
    def __init__(self, file):
        self.file_name = file
        self.encoding = 'utf-8'

    def read_conf(self):
        # 首先将yaml文件打开，以file对象赋值给conf
        conf = open(file=self.file_name, mode='r', encoding=self.encoding)
        # 然后将这个file对象进行读取
        str_conf = conf.read()
        # 这里使用yaml.Load方法将读取的结果传入进去
        dict_conf = yaml.load(stream=str_conf, Loader=yaml.FullLoader)
        # 返回数据
        return dict_conf

    # 读取配置账户里的值并赋值返回
    def access(self, item):
        name = item[0]
        region_id = item[1]
        access_key_id = item[2]
        access_key_secret = item[3]

        # print(access_key_id, access_key_secret, regionId)
        return access_key_id, access_key_secret, name, region_id
