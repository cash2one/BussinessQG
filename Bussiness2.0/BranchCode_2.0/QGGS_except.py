#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_except.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取异常名录信息，并进行更新

import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Get_BranchInfo
from PublicCode.deal_html_code import caculate_time
from PublicCode.Bulid_Log import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_py_id = sys.argv[3]

# url = 'http://www.gsxt.gov.cn/%7B5l_RJDt6qW3U2WQziG7diPLhCa1Ww-iuKP82_Fp58CFoVqh3BuQS59-Ku-xM26AJ7z2_3RfhSpDYyi0SAslpirM_EsN25JdENt3uKuyHM7g4e3EAGAFqFhhCbx-MM5jI-1501664728661%7D'
# gs_basic_id = 229418502
# gs_py_id = 1501
except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
select_except_py = 'select  updated from gs_except where gs_basic_id = %s order by updated desc  LIMIT 1'
update_except = 'update gs_except set gs_except_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,updated = %s where gs_except_id = %s'
update_except_py = 'update gs_py set gs_py_id = %s,gs_except = %s,updated =%s where gs_py_id = %s'

class Except:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            types = '经营异常'
            in_reason = singledata["speCause_CN"]
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

                count = cursor.execute(select_except, (gs_basic_id, in_date))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(except_string, (
                    gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept, updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif count == 1:
                    gs_except_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(update_except, (
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
#用于判断状态
def jude_status(recodestotal,total):
    if recodestotal == 0:
        flag = -1
    elif recodestotal == -1:
        flag = 100000004
    elif recodestotal > 0 and total >= 0 and total < 100000001:
        flag = total
    elif recodestotal > 0 and total > 100000001:
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
                recordstotal, total,insert_total,update_total = Get_BranchInfo(gs_py_id).get_info(None, gs_basic_id, cursor, connect, url, QGGS, name)
                flag = jude_status(recordstotal,total)
    except Exception, e:
        flag = 100000006
        logging.error('%s error %s' % (name, e))
    finally:
        if flag == None:
            flag ,total,insert_total,update_total,recordstotal= 0,0,0,0,0
        else:
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            cursor.execute(update_sql, (gs_py_id,flag,updated_time,gs_py_id))
            connect.commit()
        return flag,recordstotal,update_total,insert_total
def main():
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    flag,recordstotal,update_total,insert_total = update_branch3(cursor, connect, gs_basic_id, gs_py_id, select_except_py, update_except_py, Except, "except")
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