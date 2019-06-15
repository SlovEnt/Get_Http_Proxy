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
from multiprocessing import Pool
import traceback

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


def sing_verifi(proxyInfo):

    try:
        # print(proxyInfo)
        n = 0
        while n <= 3:
            n += 1
            isOk = chsp.verifi_proxy_webmasterhome(proxyInfo)
            if isOk is True:
                print("{0} {1} {2} 校验成功，返回IP为：{3}。".format(
                    proxyInfo["type"],
                    proxyInfo["ip"],
                    proxyInfo["port"],
                    isOk,
                ))
                return True

        if isOk is not True:
            print("{0} {1} {2} 校验失败，失败次数为：{4}，返回IP为：{3}。".format(
                proxyInfo["type"],
                proxyInfo["ip"],
                proxyInfo["port"],
                isOk,
                proxyInfo["weights"]
            ))

            proxyInfo["is_ok"] = "N"
            chsp.update_proxy_isok(proxyInfo)
            return False
    except Exception as e:
        # traceback.print_exc()
        print(e)



def main():

    proxyInfoList = chsp.get_proxy_list()

    p = Pool(5)
    for proxyInfo in proxyInfoList:

        # sing_verifi(proxyInfo)
        p.apply_async(sing_verifi, (proxyInfo,))

    p.close()
    p.join()    # behind close() or terminate()

if __name__ == '__main__':
    main()
