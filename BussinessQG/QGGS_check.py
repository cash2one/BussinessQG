#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import sys
import time

from deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

check_string = 'insert into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s'
update_check = 'update gs_check set types = %s ,result = %s,check_date = %s,gov_dept = %s ,updated = %s where gs_check_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        types = singledata["insType"]
        result = singledata["insRes_CN"]
        check_date = singledata["insDate"]
        check_date = change_date_style(check_date)
        gov_dept = singledata["insAuth_CN"]
        information[i] = [types, result, check_date, gov_dept]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        types, result = information[key][0], information[key][1]
        check_date, gov_dept = information[key][2], information[key][3]
        try:
            count = cursor.execute(select_check, (gs_basic_id, check_date))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(check_string,
                                            (gs_basic_id, types, result, check_date, gov_dept, updated_time))
                insert_flag += rows_count
                connect.commit()
            elif count == 1:
                gs_check_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(update_check,
                                            (types, result, check_date, gov_dept, updated_time, gs_check_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:
            # print "check error:",e
            logging.error("check error:" % e)
    flag = insert_flag + update_flag
    # print insert_flag, update_flag
    # print flag
    return flag
