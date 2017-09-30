#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report_invest.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :年报中的对外投资信息

import logging
import sys
import time
import re


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_report_py ='update gs_py set gs_py_id = %s ,report = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
update_run_py = 'update gs_py set gs_py_id = %s ,report_run = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
assure_py = 'update gs_py set gs_py_id = %s ,report_assure = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s '
invest_py = 'update gs_py set gs_py_id = %s ,report_invest = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
permit_py = 'update gs_py set gs_py_id = %s ,report_permit = %s ,updated = %s where gs_basic_id = %s and gs_py_id = %s'
schange_py = 'update gs_py set gs_py_id = %s ,report_schange = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
share_py = 'update gs_py set gs_py_id = %s,report_share = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
web_py = 'update gs_py set gs_py_id = %s,report_web = %s,updated = %s where gs_basic_id = %s and gs_py_id = %s'
class Invest:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            uuid = singledata["forInvId"]
            name = singledata["entName"]
            pattern = re.compile('^9')
            if "regNo" in singledata.keys():
                code = singledata["regNo"]
                match = re.findall(pattern,code)
                if len(match)>0:
                    code = code[0:18]
                else:
                    code = code[0:15]
            else:
                code = ''
            if "uniscId" in singledata.keys():
                ccode = singledata["uniscId"]
                ccode = ccode[0:18]
            else:
                ccode = ''
            information[i] = [name, code, ccode,uuid]
        return information


    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag = 0,0
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
            if flag < 100000001:
                remark = insert_flag
            # cursor.execute(invest_string,(remark,gs_basic_id))

            return remark,insert_flag,update_flag
