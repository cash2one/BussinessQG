#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_permit.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : 取年报中的行政许可信息并将数据插入数据库
import logging
import time

from SPublicCode.deal_html_code import change_chinese_date

permit_string = 'insert into gs_report_permit(gs_basic_id,gs_report_id,uuid,province,types,valto,created,updated)' \
                'values(%s,%s,%s,%s,%s,%s,%s,%s)'


class Permit:
    def name(self, data):
        information = {}
        for i, singledata in enumerate(data):

            uuid = singledata["annlPermitId"]
            if "licNameInterpreted" in singledata.keys():
                types = singledata["licNameInterpreted"]
            else:
                types = ''
            if "valTo" in singledata.keys():
                valto = singledata["valTo"]
                valto = change_chinese_date(valto)
            else:
                valto = None

            information[i] = [uuid, types, valto]
        return information

    def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, information, province):
        insert_flag, update_flag = 0, 0
        remark = 0
        total = len(information)
        try:
            for key in information.keys():
                uuid, types, valto = information[key][0], information[key][1], information[key][2]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(permit_string,(gs_basic_id, gs_report_id, uuid, province, types, valto, updated_time,
                                      updated_time))
                insert_flag += flag
                connect.commit()
        except Exception, e:
            remark = 100000006
            logging("permit error %s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag

            return remark,total, insert_flag, update_flag
