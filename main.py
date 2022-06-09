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
import tc
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


def create_type_node(assets_node, access_type, cloud_name):
    jump_assets_conn = jms.NewJumpserver()
    full_vpc = list(set(assets_node.values()))
    # print(full_vpc)
    for i in full_vpc:
        a = "/Default/" + access_type + "/" + cloud_name + "/"
        full_path = a + i
        jump_assets_conn.create_node(full_path)
        # logging.info(full_path + "  VPC add")
    # assets_node.clear()
    full_vpc.clear()


def main():
    """
    1、创建VPC名的节点
    2、每个区域的主机添加到一个字典内{region1[id1:完整节点地址,id2:完整节点地址],region2[id1:完整节点地址,id2:完整节点地址]}
    3、删除不存在的资产(每个区域的资源加到一个字典里去，等最后再统一加到jump内)
    4、添加额外的资产
    """
    # 获取所有用户信息
    res = config.GetConfig('config.yaml')
    cloud_access_list = res.read_conf()
    # 循环每个账户
    global access_key_id, access_key_secret, region

    all_full_path = {}
    all_assets_dict = {}
    all_assets_ip_list = []

    for access_type in cloud_access_list:
        # 转换成列表
        access_data = [
            (d['Name'], d['RegionId'], d['AccessKeyId'], d['AccessKeySecret'])
            for d in cloud_access_list[access_type]
        ]
        for item in access_data:
            access_key_id, access_key_secret, name, region_id = res.access(item)
            name_list = name.split('-')
            name_head = name_list[0] + '-' + name_list[1]
            if access_type == "Tencent":
                print(access_type)
                for region in region_id:
                    print(region)
                    time.sleep(1)
                    assets_ip_list, assets_name_list, assets_node = tc.TencentCvm(access_key_id, access_key_secret,
                                                                                  region).vcm_info(region,
                                                                                                   name_head)
                    # 增量创建vpc名节点,不会删除原有的节点
                    create_type_node(assets_node, access_type, name)
                    assets_dict = dict(list(zip(assets_ip_list, assets_name_list)))
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

            if access_type == "Aliyun":
                print(access_type)
                for region in region_id:
                    print(region)
                    time.sleep(1)
                    assets_ip_list, assets_name_list, assets_node = aliyun.AliyunEcs(access_key_id, access_key_secret,
                                                                                     region).ecs_info(region,
                                                                                                      name_head)
                    # 增量创建vpc名节点,不会删除原有的节点
                    create_type_node(assets_node, access_type, name)
                    assets_dict = dict(list(zip(assets_ip_list, assets_name_list)))
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
                    assets_ip_list, assets_name_list, assets_node = aws.AwsEc2(access_key_id,
                                                                               access_key_secret,
                                                                               region).ec2_info(
                        region, name_head)
                    # 增量创建vpc名节点,不会删除原有的节点
                    create_type_node(assets_node, access_type, name)
                    assets_dict = dict(list(zip(assets_ip_list, assets_name_list)))
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
    # 取 ip = id
    jump_ip_dict, _ = diff.Diff(all_assets_ip_list, white_list_ip).all_assets()
    # 取 ip = hostname
    _, jump_hostname_dict = diff.Diff(all_assets_ip_list, white_list_ip).all_assets()
    # 对比相同value，取不同的key
    diff_dict = all_assets_dict.keys() & jump_hostname_dict
    # 对比相同key，取不同value对应的字典
    diff_valss = [(k, all_assets_dict[k]) for k in diff_dict if all_assets_dict[k] != jump_hostname_dict[k]]
    diff_list = [k for k, _ in diff_valss]

    delete_ip_list = [ip for ip in jump_ip_dict if ip not in all_assets_ip_list + white_list_ip] + diff_list
    if len(delete_ip_list) > 0:
        for ip in delete_ip_list:
            del_assets = jms.NewJumpserver().delete_assets(id=jump_ip_dict[ip])
            logging.info(ip + " removed")
            print(ip + " removed")

    add_ip_list = [ip for ip in all_assets_ip_list if ip not in jump_hostname_dict] + diff_list
    for ip in add_ip_list:
        hostname = all_assets_dict[ip]
        full_path = all_full_path[ip]
        jms.NewJumpserver().create_assets(ip=ip, hostname=hostname,
                                          full_path=full_path)
        logging.info(ip + " add")


if __name__ == '__main__':
    main()
