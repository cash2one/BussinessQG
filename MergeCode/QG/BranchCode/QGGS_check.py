#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_check.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取抽查检查信息并进行更新


import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.deal_html_code import caculate_time
from PublicCode.Public_code import Get_BranchInfo


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



check_string = 'insert  into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s and types = %s'
select_check_py = 'select  updated from gs_check where gs_basic_id = %s order by updated desc  LIMIT 1'
class Check:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            types = singledata["insType"]
            if types == '1':
                types = '抽查'
            else:
                types = '检查'
            result = singledata["insRes_CN"]
            check_date = singledata["insDate"]
            check_date = change_date_style(check_date)
            gov_dept = singledata["insAuth_CN"]
            information[i] = [types, result, check_date, gov_dept]
        return information


    def update_to_db(self,gs_basic_id,information):
        insert_flag,update_flag = 0,0
        flag = 0
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                types, result = information[key][0], information[key][1]
                check_date, gov_dept = information[key][2], information[key][3]

                count = cursor.execute(select_check, (gs_basic_id, check_date,types))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                    rows_count = cursor.execute(check_string,
                                                (gs_basic_id, types, result, check_date, gov_dept, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            flag = 100000006
            logging.error("check error: %s" % e)
        finally:
            cursor.close()
            connect.close()
            if flag <100000001:
                flag = insert_flag
            return flag,insert_flag,update_flag

def main(gs_basic_id,url):
    Judge(gs_basic_id, url).update_branch(Check, "check")