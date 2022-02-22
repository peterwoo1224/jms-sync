# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: aws.py
@time: 2022/1/7 17:22
"""

import boto3

assets_ip_list = []
assets_name_list = []
assets_node = {}


class GetEC2Information():
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

    def ec2_information(self, region):
        """
        :return: 获取所有账号下ec2资源信息
        """
        ec2 = self.ec2_client(self.access_key_id, self.access_key_secret, self.region)
        instances = ec2.describe_instances()
        for item in instances['Reservations']:
            for instance in item['Instances']:
                state = instance['State']['Name']
                # if state != 'running':
                # AWS存在状态为terminated主机
                if state == 'terminated':
                    continue
                tags = instance.get('Tags', [])
                assets_name = ''
                for t in tags:
                    if t['Key'] == 'Name':
                        assets_name = t['Value']
                full_assets_name = region + '-' + assets_name
                assets_name_list.append(full_assets_name)
                assets_ip = instance['PrivateIpAddress']
                assets_ip_list.append(assets_ip)
                # print(full_assets_name)
                try:
                    vpcId = instance['VpcId']
                    assets_node[assets_ip] = vpcId
                except AttributeError:
                    assets_node[assets_ip] = '资产同步分类失败'
        return assets_ip_list, assets_name_list, assets_node
