__author__ = 'SlovEnt'
__date__ = '2018/10/17 14:54'
__version__ = '1.0'

import os

# 取数据库环境变量
# os.environ["nls_lang"] = "AMERICAN_AMERICA.AL32UTF8"

class cxOracle(object):

    def __init__(self, uname, upwd, tns, cx_Oracle):
        self._uname = uname
        self._upwd = upwd
        self._tns = tns
        self.cx_Oracle = cx_Oracle
        self._conn = None
        self._ReConnect()

    def _ReConnect(self):
        if not self._conn:
            self._conn = self.cx_Oracle.connect(self._uname, self._upwd, self._tns)
        else:
            pass

    def __del__(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _NewCursor(self):
        cur = self._conn.cursor()
        if cur:
            return cur
        else:
            print("#Error# Get New Cursor Failed.")
            return None

    def _DelCursor(self, cur):
        if cur:
            cur.close()

    # 检查是否允许执行的sql语句
    def _PermitedUpdateSql(self, sql):
        rt = True
        lrsql = sql.lower()
        sql_elems = [lrsql.strip().split()]

        # update和delete最少有四个单词项
        if len(sql_elems) < 4:
            rt = False
        # 更新删除语句，判断首单词，不带where语句的sql不予执行
        elif sql_elems[0] in ['update', 'delete']:
            if 'where' not in sql_elems:
                rt = False

        return rt

    # 导出结果为文件
    def Export(self, sql, file_name, colfg='||'):
        rt = self.Query(sql)
        if rt:
            with open(file_name, 'a') as fd:
                for row in rt:
                    ln_info = ''
                    for col in row:
                        ln_info += str(col) + colfg
                    ln_info += '\n'
                    fd.write(ln_info)

    # 查询
    def Query(self, sql, nStart=0, nNum=- 1):
        rt = []

        # 获取cursor
        cur = self._NewCursor()
        if not cur:
            return rt

        # 查询到列表
        cur.execute(sql)
        if (nStart == 0) and (nNum == 1):
            rt.append(cur.fetchone())
        else:
            rs = cur.fetchall()
            if nNum == - 1:
                rt.extend(rs[nStart:])
            else:
                rt.extend(rs[nStart:nStart + nNum])

        # 释放cursor
        self._DelCursor(cur)

        return rt

    # 字段名
    def QueryDesc(self, sql, nStart=0, nNum=- 1):
        rt = []

        # 获取cursor
        cur = self._NewCursor()
        if not cur:
            return rt

        # 查询到列表
        cur.execute(sql)
        descList = [i[0] for i in cur.description]

        # 释放cursor
        self._DelCursor(cur)

        return descList

    # 更新
    def Exec(self, sql):
        # 获取cursor
        rt = None
        cur = self._NewCursor()
        if not cur:
            return rt

        # 判断sql是否允许其执行
        # if not self._PermitedUpdateSql(sql):
        #     return rt

        # 执行语句
        rt = cur.execute(sql)

        # 提交事物
        self._conn.commit()

        # 释放cursor
        self._DelCursor(cur)

        return rt

    def QueryDict(self, sql, nStart=0, nNum=- 1):

        rt = []

        cur = self._NewCursor()
        if not cur:
            return rt

        cur.execute(sql)

        descList = [i[0] for i in cur.description]

        if (nStart == 0) and (nNum == 1):
            dataList = cur.fetchone()
            singDataDict = {}
            for x in range(0, len(descList) - 1):
                singDataDict[descList[x]] = dataList[x]
                rt.append(singDataDict)

        else:

            rs = cur.fetchall()
            rsDict = []

            for r in rs:
                singDataDict = {}
                for x in range(0, len(descList)):
                    singDataDict[descList[x]] = r[x]
                rsDict.append(singDataDict)

            if nNum == - 1:
                rt.extend(rs[nStart:])
            else:
                rt.extend(rs[nStart:nStart + nNum])

        self._DelCursor(cur)

        return rsDict

