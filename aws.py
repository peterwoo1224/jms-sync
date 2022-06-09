# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: aws.py
@time: 2022/1/7 17:22
"""

# -*- coding: utf-8 -*-
# @Time    : 2021/3/11 11:25 上午
# @Author  : peterwoo1224
# @Email   : peterwoo1224@gmail.com
# @File    : aliyun.py
# @Software: PyCharm

import boto3

# import json
# import requests
# import time
# from pypinyin import lazy_pinyin
# import pandas as pd
# import os
# from httpsig.requests_auth import HTTPSignatureAuth
#
# from pprint import pprint
# from collections import Counter

assets_ip_list = []
assets_name_list = []
assets_node = {}


class AwsEc2():
    def __init__(self, access_key_id, access_key_secret, region):
        self.region = region
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def ec2_client(self, access_key_id, access_key_secret, region):
        """
        :param id: aws_access_key_id
        :param key: aws_secret_access_key
        :param region: region_name
        :return: 建立一个与 ec2 的连接
        """
        ec2 = boto3.client(
            'ec2',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            region_name=region
        )
        return ec2

    def ec2_info(self, region, name_head):
        """
        :return: 获取所有账号下ec2资源信息
        """
        response = self.ec2_client(self.access_key_id, self.access_key_secret, self.region)
        instances = response.describe_instances()
        for item in instances['Reservations']:
            for instance in item['Instances']:
                state = instance['State']['Name']
                if state == 'terminated':
                    continue
                tags = instance.get('Tags', [])
                assets_name = ''
                for t in tags:
                    if t['Key'] == 'Name':
                        assets_name = t['Value']
                assets_ip = instance['PrivateIpAddress']
                assets_ip_list.append(assets_ip)
                full_assets_name = name_head + '-' + region + '-' + assets_name + '-' + assets_ip
                assets_name_list.append(full_assets_name)
                try:
                    vpcId = instance['VpcId']
                    assets_node[assets_ip] = vpcId
                except AttributeError:
                    assets_node[assets_ip] = '资产同步分类失败'
        return assets_ip_list, assets_name_list, assets_node