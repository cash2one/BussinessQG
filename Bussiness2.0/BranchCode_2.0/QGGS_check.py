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
from PublicCode.Bulid_Log import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_py_id = sys.argv[3]

# url = 'http://www.gsxt.gov.cn/%7B5l_RJDt6qW3U2WQziG7diMxUP2-rhXdnQ9MExF3Dw-lEd_P_yZvQWc3L4na7EsJoawEjtUP-hxBrZyCLBCzxTVL6sK7bnXyMG8L2O1C-_WCmEvEKlyVfgOWOCuCoJsxY-1501664728670%7D'
# gs_basic_id = 229418502
# gs_py_id = 1501

check_string = 'insert  into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s and types = %s'
update_check_py = 'update gs_py set gs_py_id = %s,gs_check = %s,updated = %s where gs_py_id = %s'
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


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag,update_flag = 0,0
        flag = 0
        try:
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
            if flag <100000001:
                flag = insert_flag
            return flag,insert_flag,update_flag
#用于判断状态
def jude_status(recodestotal,total):

    if recodestotal == 0:
        flag = -1
    elif recodestotal == -1:
        flag = 100000004
    elif recodestotal > 0 and total >= 0 and total < 100000001:
        flag = total

    elif recodestotal > -1 and total > 100000001:
        flag = 100000006

    return flag
def update_branch3(cursor,connect,gs_basic_id,gs_py_id,select_sql,update_sql,QGGS,name):
    try:
        now_time = time.time()
        select_string = select_sql % gs_basic_id
        last_time = cursor.execute(select_string)
        if last_time == 0:
            recordstotal, total,insert_total,update_total = Get_BranchInfo(gs_py_id).get_info(None, gs_basic_id, cursor, connect, url, QGGS, name)
            flag = jude_status(recordstotal,total)
        elif int(last_time) == 1:
            last_time = cursor.fetchall()[0][0]
            interval = caculate_time(str(now_time), str(last_time))
            if interval < 2592000:
                flag = None
            else:
                recordstotal, total, insert_total, update_total = Get_BranchInfo(gs_py_id).get_info(None, gs_basic_id, cursor, connect, url, QGGS, name)
                flag,recordstotal,update_total,insert_total= jude_status(recordstotal,total,insert_total,update_total)
    except Exception, e:
        flag = 100000006
        logging.error('%s error %s' % (name, e))
    finally:
        if flag == None:
            flag = 0
            recordstotal,update_total,insert_total = 0,0,0
        else:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_sql, (gs_py_id,flag,updated_time,gs_py_id))
            connect.commit()
        return flag,recordstotal,update_total,insert_total
def main():
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    flag,recordstotal,update_total,insert_total = update_branch3(cursor, connect, gs_basic_id,gs_py_id, select_check_py, update_check_py, Check, "check")
    cursor.close()
    connect.close()
    info = {
        "flag": 0,
        "total": 0,
        "update": 0,
        "insert": 0,
        'totalpage': 0,
        'perpage': 0
    }
    info["flag"] = int(flag)
    info["total"] = int(recordstotal)
    info["update"] = int(update_total)
    info["insert"] = int(insert_total)
    print info

if __name__ =="__main__":
    main()