#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report_permit.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :年报行政许可信息

import logging
import sys
import time
from SPublicCode.deal_html_code import change_date_style


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

permit_string = 'insert into gs_report_permit(gs_basic_id,gs_report_id,uuid,province,types,valto,created,updated)' \
                'values(%s,%s,%s,%s,%s,%s,%s,%s)'
class Permit:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            uuid = singledata["licId"]
            types = singledata["licName_CN"]
            valto = singledata["valTo"]
            valto = change_date_style(valto)
            information[i] = [uuid, types, valto]
        return information
    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag = 0,0
        remark = 0
        try:
            for key in information.keys():
                uuid, types, valto = information[key][0], information[key][1], information[key][2]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(gs_basic_id, gs_report_id, uuid, province, types, valto,updated_time,updated_time)
                insert_flag += flag
                connect.commit()
        except Exception, e:
            remark = 100000001
            logging("permit error %s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag

            return remark,insert_flag,update_flag

