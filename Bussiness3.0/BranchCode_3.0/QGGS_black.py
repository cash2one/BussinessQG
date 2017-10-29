#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_black.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取加入异常名录的黑名单信息，并进行更新


import sys
import logging
from PublicCode.deal_html_code import change_date_style
import time
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Get_BranchInfo
from PublicCode.deal_html_code import caculate_time
from PublicCode.Bulid_Log import Log
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


black_string = 'insert into gs_black(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_black = 'select gs_black_id from gs_black where gs_basic_id = %s and in_date = %s and in_reason = %s'
update_black = 'update gs_black set gs_black_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,updated = %s where gs_black_id = %s'
update_black_py = 'update gs_py set gs_py_id = %s,gs_black = %s,updated =%s where gs_py_id = %s'
select_black_py = 'select  updated from gs_black where gs_basic_id = %s order by updated desc  LIMIT 1'

update_black_py = 'update gs_py set gs_py_id = %s,gs_black = %s,updated =%s where  gs_py_id = %s'

class Black:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            types = '黑名单'
            in_reason = singledata["serILLRea_CN"]
            in_date = singledata["abntime"]
            in_date = change_date_style(in_date)
            out_reason = singledata["remExcpRes_CN"]
            out_date = singledata["remDate"]
            out_date = change_date_style(out_date)
            gov_dept = singledata["decOrg_CN"]
            information[i] = [types, in_reason, in_date, out_reason, out_date, gov_dept]
        return information
    def update_to_db(self,gs_basic_id, cursor, connect, information):
        update_flag, insert_flag = 0, 0
        remark = 0
        try:
            for key in information.keys():
                types, in_reason, in_date = information[key][0], information[key][1], information[key][2]
                out_reason, out_date, gov_dept = information[key][3], information[key][4], information[key][5]

                count = cursor.execute(select_black, (gs_basic_id, in_date,in_reason))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(black_string, (
                    gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept, updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif count == 1:
                    gs_except_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(update_black, (
                        gs_except_id,types, in_reason,  out_reason, out_date, gov_dept, updated_time, gs_except_id))
                    update_flag += rows_count
                    connect.commit()
        except Exception, e:
                remark = 100000006
                logging.error("except error: %s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag+update_flag

            return remark,insert_flag,update_flag
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
    update_total,insert_total = 0,0
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
                recordstotal, total,update_total,insert_total = Get_BranchInfo(gs_py_id).get_info(None, gs_basic_id, cursor, connect, url, QGGS, name)
                flag = jude_status(recordstotal,total,update_total,insert_total)
    except Exception, e:
        flag = 100000006
        logging.error('%s error %s' % (name, e))
    finally:
        if flag == None:
            flag,total,insert_total,update_total = 0,0,0,0
        else:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_sql, (gs_py_id,flag,updated_time,gs_py_id))
            connect.commit()
        return flag,recordstotal,update_total,insert_total
def main():
    
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    flag,recordstotal,update_total, insert_total = update_branch3(cursor, connect, gs_basic_id, gs_py_id, select_black_py, update_black_py, Black, "black")
    cursor.close()
    connect.close()
    info = {
        "flag":0,
        "total":0,
        "update":0,
        "insert":0,
        "perpage":0,
        "totalpage":0
    }
    info["flag"] = int(flag)
    info["total"] =int(recordstotal)
    info["update"] = int(update_total)
    info["insert"] = int(insert_total)
    print info

