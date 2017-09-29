#!/usr/bin/env python
# -*- coding:utf-8 -*-


import logging
import sys
import time



reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'


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
    insert_flag = 0
    remark = 0
    try:
        for key in information.keys():
            name = information[key][0]
            code = information[key][1]
            ccode = information[key][2]
            uuid = information[key][3]
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            flag = cursor.execute(out_invest_string, (gs_basic_id, gs_report_id,province, name, code, ccode, uuid, updated_time,updated_time))
            connect.commit()
            insert_flag += flag
    except Exception, e:
        remark = 100000001
        logging.error('invest error %s' % e)
    finally:
        if remark < 100000001:
            remark = insert_flag
        # cursor.execute(invest_string,(remark,gs_basic_id))

        return remark
