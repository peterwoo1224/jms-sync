# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: aliyun.py
@time: 2022/1/4 11:01
"""

import json
import requests
import time
from pypinyin import lazy_pinyin
import pandas as pd
import os
from httpsig.requests_auth import HTTPSignatureAuth

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from collections import Counter

assets_ip_list = []
assets_name_list = []
assets_node = {}


class AliyunEcs():
    def __init__(self, access_key_id, access_key_secret, region):
        self._client = AcsClient(access_key_id, access_key_secret, region)

    def page_num(self):
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        response = json.loads(self._client.do_action_with_exception(request))
        _ecs_num = response.get('TotalCount') // 100 + 2
        return _ecs_num

    def assets_list(self,region):
        request = DescribeInstancesRequest()
        request.set_accept_format('json')
        request.set_PageSize(100)
        for item in range(1, self.page_num()):
            request.set_PageNumber(item)
            response = json.loads(self._client.do_action_with_exception(request))
            instances_list = response.get('Instances').get('Instance')
            for instance in instances_list:
                if instance.get('Status') != 'Running':
                    continue
                assets_name = instance.get('InstanceName')
                full_assets_name = region + '-' + assets_name
                assets_name_list.append(full_assets_name)
                assets_ip = ''.join(instance.get('VpcAttributes').get('PrivateIpAddress').get('IpAddress'))
                assets_ip_list.append(assets_ip)
                try:
                    vpc_id = ''.join(instance.get('VpcAttributes').get('VpcId'))
                    assets_node[assets_ip] = vpc_id
                except AttributeError:
                    assets_node[assets_ip] = '资产同步分类失败'
        return assets_ip_list, assets_name_list, assets_node
