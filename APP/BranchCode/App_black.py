#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_black.py
# @Author: Lmm
# @Date  : 2017-08-18
# @Desc  : 用于获取黑名单信息，并将信息更新至数据库中


import logging
from PublicCode.deal_html_code import change_chinese_date
from PublicCode import deal_html_code
import time
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Log


black_string = 'insert into gs_black(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_black = 'select gs_black_id from gs_black where gs_basic_id = %s and in_date = %s '
update_black = 'update gs_black set gs_black_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,updated = %s where gs_black_id = %s'
update_black_py = 'update gs_py set gs_py_id = %s,gs_black = %s,updated =%s where gs_py_id = %s'

class Black:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            types = '黑名单'
            if "bulletinListed" in singledata.keys():
                in_reason = singledata["bulletinListed"]
                in_reason = deal_html_code.remove_symbol(in_reason)
            else:
                in_reason = ''
            if "abnTime" in singledata.keys():
                in_date = singledata["abnTime"]
                in_date = change_chinese_date(in_date)
            else:
                in_date = None
            if "bulletinRemoved" in singledata.keys():
                out_reason = singledata["bulletinRemoved"]
                out_reason = deal_html_code.remove_symbol(out_reason)
            else:
                out_reason = ''

            if "remTime" in singledata.keys():
                out_date = singledata["remTime"]
                out_date = change_chinese_date(out_date)
            else:
                out_date = None
            if "remOrganInterpreted" in singledata.keys():
                gov_dept = singledata["remOrganInterpreted"]
            else:
                gov_dept = ''
            information[i] = [types, in_reason, in_date, out_reason, out_date, gov_dept]
        return information
    def update_to_db(self,gs_basic_id, cursor, connect, information):
        update_flag, insert_flag = 0, 0
        remark = 0
        total = len(information)
        logging.info('black total:%s'%total)
        try:
            for key in information.keys():
                types, in_reason, in_date = information[key][0], information[key][1], information[key][2]
                out_reason, out_date, gov_dept = information[key][3], information[key][4], information[key][5]

                count = cursor.execute(select_black, (gs_basic_id, in_date))
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
                logging.error("black error: %s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag+update_flag
                logging.info("execute black :%s"%remark)

            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().updaye_py(gs_py_id,gs_basic_id,Black,"black",data,update_black_py)