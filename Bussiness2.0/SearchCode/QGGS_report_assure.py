#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report_assure.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :年报对外担保信息

#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time
from SPublicCode.deal_html_code import change_date_style


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

assure_string = 'insert into gs_report_assure(gs_baisc_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways,created,updated) \
values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
assure_py = 'update gs_py set report_assure = %s where gs_basic_id = %s '
class Assure:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            uuid = singledata["moreId"]
            creditor = singledata["more"]
            debtor = singledata["mortgagor"]
            cates = singledata["priClaSecKind"]
            if cates == '1':
                cates = '合同'
            elif cates == '2':
                cates = '其他'

            amount = singledata["priClaSecAm"]
            pefPerForm = singledata["pefPerForm"]
            pefPerForm = change_date_style(pefPerForm)
            pefPerTo = singledata["pefPerTo"]
            pefPerTo = change_date_style(pefPerTo)
            deadline = str(pefPerForm) + '至' +str(pefPerTo)
            period = singledata["guaranperiod"]
            ways = singledata["gaType"]
            information[i] = [uuid, creditor, debtor, cates, amount, deadline, period, ways]
        return information
    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        remark = 0
        insert_flag,update_flag = 0,0
        try:
            for key in information.keys():
                uuid, creditor, debtor, cates = information[key][0],information[key][1],information[key][2],information[key][3]
                amount, deadline, period, ways = information[key][4],information[key][5],information[key][6],information[key][7]

                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(assure_string,(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways, updated_time, updated_time))
                insert_flag += flag
                connect.commit()
        except Exception, e:
            remark = 100000001
            logging.error("report assure error:%s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag