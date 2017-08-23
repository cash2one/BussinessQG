#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : App_report_assure.py
# @Author: Lmm
# @Date  : 2017-08-09
# @Desc  : 获取App接口中的对外担保信息
import logging
import sys
import time

from PublicCode.deal_html_code import change_chinese_date

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

assure_string = 'insert into gs_report_assure(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt,created,updated) \
values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Assure:
    def name(self,data):
        information = {}
        for i,singledata in enumerate(data):
            uuid = singledata["annlFwarnntId"]
            creditor = singledata["more"]
            debtor = singledata["mortgagor"]
            cates = singledata["priClaSecKindInterpreted"]

            amount = singledata["priClaSecAm"]
            if 'pefPerForm' in singledata.keys():
                pefPerForm = singledata["pefPerForm"]
                pefPerForm = change_chinese_date(pefPerForm)
            else:
                pefPerForm = None
            if "pefPerTo" in singledata.keys():
                pefPerTo = singledata["pefPerTo"]
                pefPerTo = change_chinese_date(pefPerTo)
            else:
                pefPerTo = None
            if pefPerForm ==None:
                pefPerForm = ''
            if pefPerTo  == None:
                pefPerTo = ''

            deadline = str(pefPerForm) + '至' +str(pefPerTo )
            period = singledata["guaranPeriodInterpreted"]
            ways = singledata["gaTypeInterpreted"]
            if_fwarnnt = int(singledata["fwarnntSign"])
            information[i] = [uuid, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt]
        return information
    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        remark = 0
        insert_flag,update_flag = 0,0
        total = len(information)
        try:
            for key in information.keys():
                uuid, creditor, debtor, cates = information[key][0],information[key][1],information[key][2],information[key][3]
                amount, deadline, period, ways = information[key][4],information[key][5],information[key][6],information[key][7]
                if_fwarnnt = information[key][8]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(assure_string,(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways, if_fwarnnt,updated_time, updated_time))
                insert_flag += flag
                connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("report assure error:%s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,total,insert_flag,update_flag



