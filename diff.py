# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: diff.py
@time: 2022/1/13 19:14
"""

import jms

jump_ip_list = []
jump_id_list = []
jump_hostname_list = []
node_dict = {}


class Diff():
    def __init__(self, assets_ip_list, white_list_ip):
        self.assets_ip_list = assets_ip_list
        self.white_list_ip = white_list_ip

    def all_node(self):
        # #jumpserver全部资产
        jump_assets_info = jms.NewJumpserver()
        for node_info in jump_assets_info.get_nodes():
            node_dict[node_info.get('value')] = node_info.get('id')
        return node_dict

    def all_assets(self):
        jump_assets_info = jms.NewJumpserver()
        for var in jump_assets_info.get_assets():
            jump_id_list.append(var.get('id'))
            jump_ip_list.append(var.get('ip'))
            jump_hostname_list.append(var.get('hostname'))
        jumpserver_dict = dict(list(zip(jump_ip_list, jump_id_list)))  # 将Jumpserver资产合并成子字典
        jumpserver_hostname_dict = dict(list(zip(jump_ip_list, jump_hostname_list)))
        return jumpserver_dict,jumpserver_hostname_dict


    def assets_full_path(self, assets_node, access_type, name):
        add_ip_list = [ip for ip in self.assets_ip_list]
        region_full_path = []
        if len(add_ip_list) > 0:
            for ip in add_ip_list:
                try:
                    node_dict = self.all_node()
                    node_id = node_dict['{}'.format(assets_node[ip])]
                    node_name = list(node_dict.keys())[list(node_dict.values()).index(node_id)]
                    full_path = "/Default/" + access_type + "/" + name + "/" + node_name
                    region_full_path.append(full_path)
                except KeyError:
                    full_path = "/Default/资产同步分类失败"
                    region_full_path.append(full_path)
            full_path_dict = dict(list(zip(add_ip_list, region_full_path)))
            return full_path_dict
