#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_invest.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : App中的对外投资信息获取
import json
import logging
import time
out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
class Invest:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            uuid = singledata["annlOutinvId"]
            name = singledata["entName"]
            if "regNo" in singledata.keys():
                code = singledata["regNo"]
            else:
                code = ''
            if "uniScid" in singledata.keys():
                ccode = singledata["uniScid"]
            else:
                ccode = ''
            information[i] = [name, code, ccode,uuid]
        return information
    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag = 0,0
        remark = 0
        total = len(information)
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
            #print code,ccode
            remark = 100000006
            logging.error('invest error %s' % e)
        finally:
            if remark < 100000001:
                remark = insert_flag

            return remark,total,insert_flag,update_flag

