# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: jms.py
@time: 2022/1/6 17:17
"""

import json
import time
import os
import pandas as pd

from httpsig.requests_auth import HTTPSignatureAuth
import requests


# jumpserver配置
key_id = '58edeb63-8ac1-4a71-a095-xxxxx'
secret = 'b6b1d83f-efae-4741-bc6b-xxxxx'
jumpserver_url = 'https://jump.xxxxx.com'
admin_user = '3fa85f64-5717-4562-b3fc-xxxxx'

class NewJumpserver():
    def __init__(self, host=jumpserver_url, key_id=key_id, secret=secret):
        self.host = host
        self.keyid = key_id
        self.secret = secret
        self.node_list = self.get_node_list()

    def _auth(self):
        signature_headers = ['(request-target)', 'accept', 'date', 'host']
        auth = HTTPSignatureAuth(key_id=self.keyid, secret=self.secret,
                                 algorithm='hmac-sha256',
                                 headers=signature_headers)
        return auth

    def _headers(self):
        headers = {
            'Accept': 'application/json',
            'Date': str(time.strftime("%a %b %d %H:%M:%S %Y", time.localtime()))
        }
        return headers

    def get_assets(self):
        url = self.host + '/api/v1/assets/assets/'
        req = requests.get(url, auth=self._auth(), headers=self._headers())
        return json.loads(req.content)

    def update_node_list(self):
        self.node_list = self.get_node_list()

    # 获取节点
    def get_node_list(self):
        url = self.host + '/api/v1/assets/nodes/'
        req = requests.get(url, auth=self._auth(), headers=self._headers())
        node_list_json = json.loads(req.content.decode())
        node_list_df = pd.DataFrame.from_records(
            node_list_json, columns=["id", "name", "full_value", "key"])
        node_list_df["full_value"] = node_list_df["full_value"].str.replace(
            " ", "")
        return node_list_df

    def get_nodes(self):
        url = self.host + '/api/v1/assets/nodes/'
        req = requests.get(url, auth=self._auth(), headers=self._headers())
        return json.loads(req.content)

    # 创建节点
    def create_node(self, full_path):
        if self.get_nodeid_by_fullpath(full_path):
            print("%s exsists" % full_path)
            return

        name = os.path.basename(full_path)
        f_path = os.path.dirname(full_path)
        f_nodeid = self.get_nodeid_by_fullpath(f_path)

        if not f_nodeid:
            print("父节点 %s 不存在" % f_path)
            exit(9)
        data = {
            "name": name,
            "value": name
        }
        print(data)
        url = jumpserver_url + '/api/v1/assets/nodes/{}/children/'.format(f_nodeid)
        req = requests.post(url, auth=self._auth(), headers=self._headers(), data=data)
        if req.status_code == 201:
            print("%s Create SUCCESSED" % full_path)
            self.update_node_list()
        else:
            print("%s Create FALIED" % full_path, req.content.decode())

    # 创建资产
    def create_assets(self, ip, full_path, hostname):

        node_id = self.get_nodeid_by_fullpath(full_path)
        if not node_id:
            print("没有找到对应节点 %s" % full_path)
            exit(10)
        # ip_list = [line.strip() for line in ip_str.strip().split("n")]
        #
        # for ip in ip_list:
        data = {
            "ip": ip,
            "hostname": hostname,
            "platform": "Linux",
            "admin_user": admin_user,
            "admin_user_display": "root",
            "protocols": ["ssh/22"],
            "created_by": "Administrator",
            "nodes": node_id,
            "is_active": 'true',
        }
        url = self.host + '/api/v1/assets/assets/'
        req = requests.post(url, auth=self._auth(), headers=self._headers(), data=data)
        if req.status_code == 201:
            print("%s add into %s SUCCESSED" % (ip, full_path))
        else:
            print("%s add into %s FALIED" % (ip, full_path))

    # 获取节点id
    def get_nodeid_by_fullpath(self, full_path=None):
        node_id = self.node_list["full_value"] == full_path
        if node_id.any():
            return self.node_list[node_id]["id"].str.cat()
        else:
            return None

    def delete_assets(self, id):
        # /assets/nodes/{id}/
        url = jumpserver_url + '/api/v1/assets/assets/{}/'.format(id)
        req = requests.delete(url, auth=self._auth(), headers=self._headers())
        return req.content.decode('utf-8')
