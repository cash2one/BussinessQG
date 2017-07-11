#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
update_except = 'update gs_except set types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,updated = %s where gs_except_id = %s'
def name(data):
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


def update_to_db(gs_basic_id, cursor, connect, information):
    update_flag, insert_flag = 0, 0
    for key in information.keys():
        types, in_reason, in_date = information[key][0], information[key][1], information[key][2]
        out_reason, out_date, gov_dept = information[key][3], information[key][4], information[key][5]
        try:

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
                types, in_reason,  out_reason, out_date, gov_dept, updated_time, gs_except_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:

            logging.error("except error: %s" % e)
    flag = insert_flag + update_flag
    return flag
