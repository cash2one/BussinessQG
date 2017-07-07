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

out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_out_invest = 'select gs_report_invest_id from gs_report_invest where gs_report_id = %s and name = %s'
update_out_invest = 'update gs_report_invest set code = %s ,ccode = %s,uuid = %s,updated = %s where gs_report_invest_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        uuid = singledata["forInvId"]
        name = singledata["entName"]
        if "uniscId" in singledata.keys():
            code = singledata["uniscId"]
        else:
            code = None
        if "regNo" in singledata.keys():
            ccode = singledata["regNo"]
        else:
            ccode = None
        information[i] = [name, code, ccode,uuid]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information,province):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name = information[key][0]
        code = information[key][1]
        ccode = information[key][2]
        uuid = information[key][3]
        try:
            count = cursor.execute(select_out_invest, (gs_report_id, name))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(out_invest_string, (gs_basic_id, gs_report_id,province, name, code, ccode, uuid, updated_time,updated_time))
                connect.commit()
                insert_flag += flag
            elif int(count) == 1:
                gs_report_invest_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_out_invest, (code,ccode,uuid, updated_time, gs_report_invest_id))
                connect.commit()
                update_flag += flag
        except Exception, e:
            logging.error('out_invest error %s ' % e)
    total = insert_flag + update_flag
    return total
