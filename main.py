# -*- coding: utf-8 -*-

"""
@author: peterwoo
@software: PyCharm
@file: main.py
@time: 2022/1/7 15:10
"""

import config
import jms
import aliyun
import aws
import diff
import time

import logging
from logging.handlers import TimedRotatingFileHandler

# 定义日志
LOG_FILE = "./jms-sync.log"
logger = logging.getLogger()  # 创建logger
logger.setLevel(logging.INFO)  # 设置logger日志等级
fh = TimedRotatingFileHandler(LOG_FILE, when='D', interval=1, backupCount=30)  # 创建handler
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = '%(asctime)s %(levelname)s %(message)s '
formatter = logging.Formatter(format_str, datefmt)  # 设置输出日志格式
fh.setFormatter(formatter)  # 为handler指定输出格式
logger.addHandler(fh)  # 为logger添加的日志处理器


assets_ip_list = []
assets_name_list = []
assets_node = {}
white_list_ip = ['192.168.51.200', ]


def create_type_node(assets_node, access_type, name):
    jump_assets_info = jms.NewJumpserver()
    full_vpc = list(set(assets_node.values()))
    # print(full_vpc)
    for i in full_vpc:
        a = "/Default/" + access_type + "/" + name + "/"
        full_path = a + i
        jump_assets_info.create_node(full_path)
        logging.info(full_path + "  VPC add")
    full_vpc.clear()


def main():
    """
    1、创建VPC名的节点
    2、每个区域的主机添加到一个字典内{region1[id1:完整节点地址,id2:完整节点地址],region2[id1:完整节点地址,id2:完整节点地址]}
    3、删除不存在的资产(每个区域的资源加到一个字典里去，等最后再统一加到jump内)
    4、添加额外的资产
    """
    # 获取所有用户信息
    access_list = config.GetConfig.parse_account('config.json')
    # 循环每个账户
    global access_key_id, access_key_secret, region

    all_full_path = {}
    all_assets_dict = {}
    all_assets_ip_list = []

    for access_type in access_list:
        # 转换成列表
        access_data = [
            (d['Name'], d['RegionId'], d['AccessKeyId'], d['AccessKeySecret'])
            for d in access_list[access_type]
        ]
        for item in access_data:
            access_key_id, access_key_secret, name, region_id = config.GetConfig.access(item)
            # print(access_key_id, access_key_secret, name, regionId)
            if access_type == "Aliyun":
                print(access_type)
                for region in region_id:
                    print(region)
                    time.sleep(1)
                    assets_ip_list, assets_name_list, assets_node = aliyun.AliyunEcs(access_key_id, access_key_secret,
                                                                                     region).assets_list(region)
                    # 增量创建vpc名节点,不会删除原有的节点
                    create_type_node(assets_node, access_type, name)
                    assets_dict = dict(list(zip(assets_ip_list, assets_name_list)))
                    # print(assets_dict)
                    region_full_path = diff.Diff(assets_ip_list, white_list_ip).assets_full_path(assets_node,
                                                                                                 access_type,
                                                                                                 name)
                    if region_full_path:
                        all_full_path.update(region_full_path)
                    all_assets_dict.update(assets_dict)
                    all_assets_ip_list.extend(assets_ip_list)
                    assets_ip_list.clear()
                    assets_name_list.clear()
                    assets_node.clear()
                    assets_dict.clear()

            elif access_type == "Aws":
                for region in region_id:
                    print(region)
                    time.sleep(1)
                    assets_ip_list, assets_name_list, assets_node = aws.GetEC2Information(access_key_id,
                                                                                          access_key_secret,
                                                                                          region).ec2_information(
                        region)
                    # 增量创建vpc名节点,不会删除原有的节点
                    create_type_node(assets_node, access_type, name)
                    assets_dict = dict(list(zip(assets_ip_list, assets_name_list)))
                    # print(assets_dict)
                    region_full_path = diff.Diff(assets_ip_list, white_list_ip).assets_full_path(assets_node,
                                                                                                 access_type,
                                                                                                 name)
                    if region_full_path:
                        all_full_path.update(region_full_path)
                    all_assets_dict.update(assets_dict)
                    all_assets_ip_list.extend(assets_ip_list)
                    assets_ip_list.clear()
                    assets_name_list.clear()
                    assets_node.clear()
                    assets_dict.clear()

    jump_ip_list = diff.Diff(all_assets_ip_list, white_list_ip).all_assets()
    add_ip_list = [ip for ip in all_assets_ip_list if ip not in jump_ip_list]

    delete_ip_list = [ip for ip in jump_ip_list if ip not in all_assets_ip_list + white_list_ip]
    if len(delete_ip_list) > 0:
        for ip in delete_ip_list:
            del_assets = jms.NewJumpserver().delete_assets(id=jump_ip_list[ip])
            logging.info(ip + " removed")
            # print(ip+" removed")

    # print(add_ip_list)
    for ip in add_ip_list:
        hostname = all_assets_dict[ip] + '-' + ip
        full_path = all_full_path[ip]
        jms.NewJumpserver().create_assets(ip=ip, hostname=hostname,
                                          full_path=full_path)
        logging.info(ip + " add")


if __name__ == '__main__':
    main()
