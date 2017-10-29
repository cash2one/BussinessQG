#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Judge_Status.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于判断更新过程中的状态

import sys
import time
from Public_code import Get_BranchInfo
import config
from Public_code import Connect_to_DB
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
class Judge:
    def __init__(self,gs_py_id,connect,cursor,gs_basic_id,url,page,perpage):
        self.gs_py_id = gs_py_id
        self.connect = connect
        self.cursor = cursor
        self.gs_basic_id = gs_basic_id
        self.url = url
        self.page = page
        self.perpage = perpage
    def jude_status(self,recodestotal,total):
        if recodestotal == 0:
            flag = -1
        elif recodestotal == -1:
            flag = 100000004
        elif recodestotal > 0 and total >= 0 and total < 100000001:
            flag = total
        elif recodestotal >-1 and total > 100000001:
            flag = 100000006
        return flag
    #对branch,permit punish,freeze,stock,brand,mort,shareholder表的更新情况做判断
    def update_branch(self,update_sql,QGGS,name):

        if name == 'share' or name == 'brand' or name =='branch':

            recordstotal, total,insert_total,update_total,totalpage,perpage = Get_BranchInfo(self.gs_py_id).get_singleinfo(None, self.gs_basic_id,self.cursor,self.connect,self.url, QGGS,name,self.page,self.perpage)
        else:
            totalpage, perpage = 0, 0
            if name =='change':
                recordstotal,total,insert_total,update_total = Get_BranchInfo(self.gs_py_id).get_info(None,self.gs_basic_id,self.cursor,self.connect,self.url[0], QGGS,name)
                if recordstotal<=0:
                    recordstotal, total, insert_total, update_total = Get_BranchInfo(self.gs_py_id).get_info(None,self.gs_basic_id,self.cursor,self.connect,self.url[1],QGGS,name)
            else:
                recordstotal, total, insert_total, update_total=Get_BranchInfo(self.gs_py_id).get_info(None, self.gs_basic_id, self.cursor, self.connect, self.url,QGGS, name)
        flag = self.jude_status(recordstotal,total)
        if flag!=-1:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_sql, (self.gs_py_id,flag, updated_time,self.gs_py_id))
            connect.commit()
            cursor.close()
            connect.close()
            
        # return flag,recordstotal,update_total,insert_total,totalpage,perpage
        self.print_info(flag,recordstotal,update_total,insert_total,totalpage,perpage,self.page)

    def print_info(self,flag,recordstotal,update_total,insert_total,totalpage,perpage,rspage):

        info = {
            "flag": 0,
            "total": 0,
            "update": 0,
            "insert": 0,
            'totalpage': 0,
            'perpage': 0,
            'rspage':1
        }
        rspage = int(rspage)
        totalpage = int(totalpage)
        if rspage >= totalpage:
            rspage = 0
        info["flag"] = int(flag)
        info["total"] = int(recordstotal)
        info["update"] = int(update_total)
        info["insert"] = int(insert_total)
        info["totalpage"] = int(totalpage)
        info["perpage"] = int(perpage)
        info["rspage"] = int(rspage)
        print info
