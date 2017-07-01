#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import logging
import sys
import time

import QGGS_Report

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,id,name,code,updated) values(%s,%s,%s,%s,%s,%s)'
select_out_invest = 'select gs_report_invest_id from gs_report_invest where gs_report_id = %s and name = %s'
update_out_invest = 'update gs_report_invest set name = %s,code = %s ,updated = %s where gs_report_invest_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["entName"]
        code = singledata["uniscId"]
        information[i] = [name, code]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name = information[key][0]
        code = information[key][1]
        m = hashlib.md5()
        m.update(str(gs_basic_id) + str(gs_report_id) + '1')
        id = m.hexdigest()
        try:
            count = cursor.execute(select_out_invest, (gs_report_id, name))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(out_invest_string, (gs_basic_id, gs_report_id, id, name, code, updated_time))
                connect.commit()
                insert_flag += flag
            elif int(count) == 1:
                gs_report_invest_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_out_invest, (name, code, updated_time, gs_report_invest_id))
                connect.commit()
                update_flag += flag
        except Exception, e:
            print e
            logging.error('out_invest error %s ' % e)
    total = insert_flag + update_flag
    return total
