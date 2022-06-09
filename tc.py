# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: tc.py
@time: 2022/4/19 19:39
"""

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cvm.v20170312 import cvm_client, models

assets_ip_list = []
assets_name_list = []
assets_node = {}


class TencentCvm():
    def __init__(self, access_key_id, access_key_secret, region):
        self.region = region
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret

    def vcm_client(self, access_key_id, access_key_secret, region):
        try:
            cred = credential.Credential(access_key_id, access_key_secret)
            httpProfile = HttpProfile()
            httpProfile.endpoint = "cvm.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = cvm_client.CvmClient(cred, region, clientProfile)

            req = models.DescribeInstancesRequest()
            params = {
            }
            req.from_json_string(json.dumps(params))
            resp = client.DescribeInstances(req)
            response = json.loads(resp.to_json_string())
            return response

        except TencentCloudSDKException as err:
            print(err)

    def vcm_info(self, region, name_head):
        """
        :return: 获取所有账号下ec2资源信息
        """
        response = self.vcm_client(self.access_key_id, self.access_key_secret, self.region)
        for item in response['InstanceSet']:
            assets_ip = ''.join(item.get('PrivateIpAddresses'))
            assets_ip_list.append(assets_ip)
            assets_name = item.get('InstanceName')
            full_assets_name = name_head + '-' + region + '-' + assets_name + '-' + assets_ip
            assets_name_list.append(full_assets_name)
            try:
                vpc_id = ''.join(item.get('VirtualPrivateCloud').get('VpcId'))
                assets_node[assets_ip] = vpc_id
            except AttributeError:
                assets_node[assets_ip] = '资产同步分类失败'
        return assets_ip_list, assets_name_list, assets_node
