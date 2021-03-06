#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and name = %s'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'



def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["entName"]
        code = singledata["licNo"]
        filename = singledata["licName_CN"]
        start_date = singledata["valFrom"]
        start_date = change_date_style(start_date)
        end_date = singledata["valTo"]
        end_date = change_date_style(end_date)
        content = singledata["licItem"]
        gov_dept = singledata["licAnth"]
        information[i] = [name, code, filename, start_date, end_date, content, gov_dept]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag = 0
    remark = 0
    for key in information.keys():
        name, code, filename, start_date = information[key][0], information[key][1], information[key][2], \
                                           information[key][3]
        end_date, content, gov_dept = information[key][4], information[key][5], information[key][6]
        count = cursor.execute(select_string, (gs_basic_id, name))
        m = hashlib.md5()
        m.update(code)
        id = m.hexdigest()
        try:
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(permit_string, (
                    gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, updated_time))
                insert_flag += rows_count
                connect.commit()

        except Exception, e:
            remark = 100000001
            logging.error("permit error: %s" % e)
    if remark < 100000001:
        remark = insert_flag

    return remark
