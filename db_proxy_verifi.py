# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/14 13:39'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from chpackage.global_function import chrome_get_html_all_content, get_new_headers
from chpackage import torndb
from chpackage.param_info import get_param_info
from chpackage.proc_proxy import chs_proxy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

def main():

    proxyInfoList = chsp.get_proxy_list()

    for proxyInfo in proxyInfoList:
        # print(proxyInfo)
        isOk = chsp.verifi_proxy_ipip(proxyInfo)
        if isOk is not True:
            print("{0} {1} {2} 失败。失败次数为：{4}。返回IP为：{3}。".format(
                proxyInfo["type"],
                proxyInfo["ip"],
                proxyInfo["port"],
                isOk,
                proxyInfo["weights"]
            ))
            continue





if __name__ == '__main__':
    main()
