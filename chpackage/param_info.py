# -*- coding: utf-8 -*-
__author__ = 'SlovEnt'
__date__ = '2018/10/17 14:31'
__version__ = '1.0'

import os

def get_param_info(ConfigFile):

    if os.path.isfile(ConfigFile) == False:
        raise Exception("错误，全局参数配置文件不存在")

    paramInfo = {}
    for line in open(ConfigFile,"r",encoding= 'UTF-8'):
        if line != "\n" :
            info = line.strip("\n")
            # 首字符为 # ; 等符号 视为注释
            if info.strip()[0] != "#" and info.strip()[0] != ";" and info.strip()[0] != "[" :
                # print(info.strip()[0])
                info = info.split("=")
                if len(info) == 2:
                    paramName = info[0].strip()
                    paramValue = info[1].strip()
                    paramInfo[paramName] = paramValue
    return paramInfo
