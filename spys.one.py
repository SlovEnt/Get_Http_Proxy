# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2019/6/2 10:48'

import time
import os
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from chpackage.global_function import chrome_get_html_all_content, get_new_headers
from chpackage import torndb
import traceback

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

    rtnHtmlContent = chrome_get_html_all_content(url, "Proxy address:port")

    # print(rtnHtmlContent)

    soup = BeautifulSoup(rtnHtmlContent, 'html.parser')
    proxyInfoList = soup.find_all(name="table")[1].find_all(name="tr")#.find_all(name="tr")

    for proxyInfo in proxyInfoList:

        # print(proxyInfo)

        proxyInfoDict = OrderedDict()
        # ipAddr, port, country, proxyType, anonymity = prox
        if '<font class="spy1">' not in str(proxyInfo):
            continue

        compile_rule = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
        match_list = re.findall(compile_rule, str(proxyInfo))

        if not match_list:
            continue

        # print("@@@", str(proxyInfo))
        compile_rule = r'''<tr class=".+?" onmouseout="this.style.background='#.+?'" onmouseover="this.style.background='#.+?'"><td colspan="1"><font class="spy1">.+?</font> <font class="spy14">(.+?)<script type="text/javascript">document.write.+?</script><font class="spy2">:</font>(.+?)</font></td><td colspan="1"><a href=".+?"><font class="spy1">(.+?)</font>.+?<td colspan="1"><a href=".+?"><font class=".+?">.+?</font></a></td><td colspan="1"><a href=".+?"><font class="spy14">(.+?)</font></a>'''
        match_list = re.findall(compile_rule, str(proxyInfo))

        if len(match_list) != 1:
            continue

        proxyInfoDict["ip"] = match_list[0][0]
    #     proxyInfoDict["ip"] = re.findall(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b", proxyInfo(name="td")[0].text)[0]
    #     # print(proxyInfoDict["ip"])
    #
        proxyInfoDict["port"] = match_list[0][1]
        proxyInfoDict["country"] = match_list[0][3]
        proxyInfoDict["addr"] = " "
        proxyInfoDict["type"] = match_list[0][2].lower() # 改为小写
        proxyInfoListArr.append(proxyInfoDict)

        # print(proxyInfoDict)

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

    if proxyInfoDict["ip"] == localIpaddress:
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

            proxies = {proxyInfoDict["type"]: '{0}://{1}:{2}'.format(proxyInfoDict["type"], proxyInfoDict["ip"], proxyInfoDict["port"])}
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

def main():

    # 每次调用页面返回的数量为64
    pagMaxNumOfTimes = 10
    urlList = []
    for i in range(1, pagMaxNumOfTimes+1):
        urlList.append("http://free-proxy.cz/zh/proxylist/main/{0}".format(i))

    for url in urlList:
        print(url)
        proxyInfoListArr = rtn_proxy_list(url)

        # 验证代理
        for proxyInfoDict in proxyInfoListArr:
            print(proxyInfoDict)

            if proxyInfoDict["type"] != "http" and proxyInfoDict["type"] != "https":
                continue

            isOk = verifi_proxy(proxyInfoDict)

            if isOk is not True:
                print("{0} {1} {2} 失败。返回IP为：{3}。".format(proxyInfoDict["type"], proxyInfoDict["ip"],
                                                         proxyInfoDict["port"], isOk))
                continue

            sqlStr = "SELECT * from proxy_list where ip='{0}' and port='{1}'".format(
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
            )

            rtnCnt = mysqlExe.query(sqlStr)
            if len(rtnCnt) == 1:
                continue

            sqlStr = "INSERT INTO `v2PySql`.`proxy_list` (`country`, `ip`, `port`, `addr`, `type`, `is_ok`, `weights`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', 'Y', '0');".format(
                proxyInfoDict["country"],
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
                "",
                proxyInfoDict["type"],
            )

            mysqlExe.execute(sqlStr)

            print("{0} {1} {2} 成功！！".format(proxyInfoDict["type"], proxyInfoDict["ip"],proxyInfoDict["port"]))


def spys_main():

    # 每次调用页面返回的数量为64
    pagMaxNumOfTimes = 3
    urlList = []
    for i in range(0, pagMaxNumOfTimes+1):
        urlList.append("http://spys.one/en/free-proxy-list/{0}/".format(i))
        urlList.append("http://spys.one/en/anonymous-proxy-list/{0}/".format(i))
        urlList.append("http://spys.one/en/https-ssl-proxy/{0}/".format(i))
        urlList.append("http://spys.one/en/http-proxy-list/{0}/".format(i))
        urlList.append("http://spys.one/en/non-anonymous-proxy-list/{0}/".format(i))

    for url in urlList:
        proxyInfoListArr = rtn_proxy_list(url)

        # 验证代理
        for proxyInfoDict in proxyInfoListArr:
            print(proxyInfoDict)

            if proxyInfoDict["type"] != "http" and proxyInfoDict["type"] != "https":
                continue

            isOk = verifi_proxy(proxyInfoDict)

            if isOk is not True:
                print("{0} {1} {2} 失败。返回IP为：{3}。".format(proxyInfoDict["type"], proxyInfoDict["ip"],
                                                         proxyInfoDict["port"], isOk))
                continue

            sqlStr = "SELECT * from proxy_list where ip='{0}' and port='{1}'".format(
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
            )

            rtnCnt = mysqlExe.query(sqlStr)
            if len(rtnCnt) == 1:
                continue

            sqlStr = "INSERT INTO `v2PySql`.`proxy_list` (`country`, `ip`, `port`, `addr`, `type`, `is_ok`, `weights`) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', 'Y', '0');".format(
                proxyInfoDict["country"],
                proxyInfoDict["ip"],
                proxyInfoDict["port"],
                "",
                proxyInfoDict["type"],
            )

            mysqlExe.execute(sqlStr)

            print("{0} {1} {2} 成功！！".format(proxyInfoDict["type"], proxyInfoDict["ip"],proxyInfoDict["port"]))



if __name__ == '__main__':

    '''
    http://spys.one/en/free-proxy-list/0/
    http://spys.one/en/anonymous-proxy-list/0/
    http://spys.one/en/https-ssl-proxy/0/
    http://spys.one/en/http-proxy-list/0/
    http://spys.one/en/non-anonymous-proxy-list/0/
    '''
    try:
        spys_main()
    except Exception as e:
        traceback.print_exc()
        print(e)

