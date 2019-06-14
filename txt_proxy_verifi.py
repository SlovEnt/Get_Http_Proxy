# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/13 11:56'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from chpackage.global_function import chrome_get_html_all_content, get_new_headers, get_html_all_content_proxy
from chpackage.proc_proxy import chs_proxy
from chpackage import torndb
import traceback

from chpackage.param_info import get_param_info
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(__file__)
CONFIG_INFO_FILE = "%s/%s" % (BASE_DIR, "Config.ini")
PARAINFO = get_param_info(CONFIG_INFO_FILE)

# 引入mysql操作函数
mysqlExe = torndb.Connection(
    host = "{0}:{1}".format(PARAINFO["DB_HOST"], PARAINFO["DB_PORT"]),
    database = PARAINFO["DB_NAME"],
    user = PARAINFO["USER_NAME"],
    password = PARAINFO["USER_PWD"],
)

chsp = chs_proxy(mysqlExe)


def txt_main():

    filePath = r"C:\Users\SlovEnt\Downloads\Proxy List.txt"

    proxyInfoArr = []

    with open(filePath, mode="r", encoding="utf-8") as f:
        proxyInfoList = f.readlines()
        for proxyInfo in proxyInfoList:
            proxyInfoDict = chsp.generate_db_proxy_list_dict()
            proxyInfo = proxyInfo.strip()
            proxyInfo = proxyInfo.split(":")
            proxyInfoDict["ip"] = proxyInfo[0]
            proxyInfoDict["port"] = proxyInfo[1]
            proxyInfoDict["type"] = "http"
            proxyInfoArr.append(proxyInfoDict)

    for proxyInfo in proxyInfoArr:

        # 判断信息是否再DB中存在
        rtnDate = chsp.select_proxy(proxyInfo)
        if len(rtnDate) > 0:
            print(proxyInfo, "已存在！！！")
            continue

        # 不存在 校验
        # print(proxyInfo, "开始检查！！！")

        isOk = chsp.verifi_proxy_webmasterhome(proxyInfo)

        if isOk is not True:
            print("{0} {1} {2} 失败。返回IP为：{3}。".format(proxyInfo["type"], proxyInfo["ip"],
                                                     proxyInfo["port"], isOk))
            continue

        print("{0} {1} {2} 成功。返回IP为：{3}。".format(proxyInfo["type"], proxyInfo["ip"],
                                                 proxyInfo["port"], isOk))

        # 校验通过 插入到数据库中
        chsp.insert_proxy_info(proxyInfo)


if __name__ == '__main__':
    try:
        txt_main()
    except Exception as e:
        traceback.print_exc()
        print(e)