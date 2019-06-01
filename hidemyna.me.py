# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/1 12:13'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from chpackage.global_function import chrome_get_html_all_content, get_new_headers
from chpackage import torndb

from chpackage.param_info import get_param_info
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


def rtn_proxy_list(url):

    proxyInfoListArr = []

    rtnHtmlContent = chrome_get_html_all_content(url, "proxy__t")
    soup = BeautifulSoup(rtnHtmlContent, 'html.parser')
    proxyInfoList = soup.find_all(name="table", attrs={"class": "proxy__t"})[0].find_all(name="tr")

    for proxyInfo in proxyInfoList:

        proxyInfoDict = OrderedDict()
        # ipAddr, port, country, proxyType, anonymity = prox
        if "adress" in str(proxyInfo):
            continue

        # print(str(proxyInfo))

        proxyInfoDict["ipaddress"] = proxyInfo(name="td")[0].text
        proxyInfoDict["port"] = proxyInfo(name="td")[1].text
        proxyInfoDict["country"] = proxyInfo(name="td")[2].text.strip()
        proxyInfoDict["country"] = proxyInfoDict["country"].replace('"', "")
        proxyInfoDict["country"] = proxyInfoDict["country"].replace('  ', " ")
        proxyInfoDict["type"] = proxyInfo(name="td")[4].text.lower() # 改为小写
        proxyInfoListArr.append(proxyInfoDict)

    return proxyInfoListArr

def verifi_proxy(proxyInfoDict):

    verifiUrl = "http://ip.webmasterhome.cn/"
    rtnHtmlContent = get_html_all_content(verifiUrl, "本机IP地址", "UTF-8", proxyInfoDict)
    # print(rtnHtmlContent)
    if "本机IP地址" in rtnHtmlContent:
        soup = BeautifulSoup(rtnHtmlContent, 'html.parser')
        localIpaddress = soup.find_all(name="span", attrs={"id": "ipaddr"})[0].text
        localIpaddress = localIpaddress.replace("本机IP地址：", "")
        localIpaddress = localIpaddress.replace("IP物理地址：请点击IP查看 ↑", "")
    else:
        localIpaddress = "127.0.0.1"

    if proxyInfoDict["ipaddress"] == localIpaddress:
        return True
    else:
        return localIpaddress

def get_html_all_content(url, pageFlag, encode, proxyInfoDict):
    '''
    :param url:  网址
    :param pageFlag: 爬取页面标识（特征，确认正确获取页面）
    :return:
    '''
    # time.sleep(2)
    getFlag = False
    n = 0
    html = "-----------------"
    while getFlag == False:
        try:
            n += 1

            headers = get_new_headers(url)

            proxies = {proxyInfoDict["type"]: '{0}://{1}:{2}'.format(proxyInfoDict["type"], proxyInfoDict["ipaddress"], proxyInfoDict["port"])}
            # print(proxies)

            r = requests.get(url=url, headers=headers, timeout=30, verify=False, proxies=proxies)
            r.raise_for_status()

            html = r.content.decode(encode, 'ignore')

            if pageFlag not in html:
                  raise Exception("页面内容获取失败！！")
            else:
                getFlag = True

        except Exception as e:
            print(url, e)
            print(html)
            if n > 3 :
                getFlag = False
                time.sleep(5)
            else:
                getFlag = True
    return html


if __name__ == '__main__':

    '''
    https://hidemyna.me/en/proxy-list/#list
    https://hidemyna.me/en/proxy-list/?start=128#list
    '''

    # 每次调用页面返回的数量为64
    pagMaxNumOfTimes = 10
    urlList = []
    for i in range(0, pagMaxNumOfTimes):
        rtnProxyNum = 64 * i

        if rtnProxyNum == 0 :
            urlList.append("https://hidemyna.me/en/proxy-list/{0}#list".format(""))
        else:
            urlList.append("https://hidemyna.me/en/proxy-list/?start={0}#list".format(rtnProxyNum))

    for url in urlList:
        proxyInfoListArr = rtn_proxy_list(url)

        # 验证代理
        for proxyInfoDict in proxyInfoListArr:

            if proxyInfoDict["type"] != "http" and proxyInfoDict["type"] != "https":
                continue

            isOk = verifi_proxy(proxyInfoDict)

            if isOk is not True:
                print("{0} {1} {2} 失败。返回IP为：{3}。".format(proxyInfoDict["type"], proxyInfoDict["ipaddress"],
                                                         proxyInfoDict["port"], isOk))
                continue

            sqlStr = "SELECT * from proxy_list where ip='{0}' and port='{1}'".format(
                proxyInfoDict["ipaddress"],
                proxyInfoDict["port"],
            )

            rtnCnt = mysqlExe.query(sqlStr)
            if len(rtnCnt) == 1:
                continue

            sqlStr = "INSERT INTO `v2PySql`.`proxy_list` (`country`, `ip`, `port`, `addr`, `type`, `is_ok`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', 'Y');".format(
                proxyInfoDict["country"],
                proxyInfoDict["ipaddress"],
                proxyInfoDict["port"],
                "",
                proxyInfoDict["type"],
            )

            mysqlExe.execute(sqlStr)

            print("{0} {1} {2} 成功！！".format(proxyInfoDict["type"], proxyInfoDict["ipaddress"],proxyInfoDict["port"]))
