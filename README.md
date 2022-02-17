# jms-sync

jumpserver同步云厂商资源脚本

1、先部署jumpserver堡垒机

2、在资产里添加节点Aliyun、AWS、资产同步分类失败父节点

3、在对应的父节点创建对应账户下节点如aliyun-hz-xxxx(完成路径为/Default/Aliyun/aliyun-hz-xxxx)

4、配置完jms.py内的一些参数与config.json

5、直接运行main.py文件