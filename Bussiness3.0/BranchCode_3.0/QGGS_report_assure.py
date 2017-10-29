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
from PublicCode.deal_html_code import change_date_style


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

assure_string = 'insert into gs_report_assure(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt,created,updated) \
values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
assure_py = 'update gs_py set report_assure = %s where gs_basic_id = %s '
class Assure:
    def name(self,data):
        info = {}
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
            if_fwarnnt = singledata["moreDis"]
            if if_fwarnnt =="2":
                if_fwarnnt = 0
            info[i] = [uuid, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt]
        return info
    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, info,province):
        remark = 0
        insert_flag, update_flag = 0, 0
        total = len(info)
        try:
            for key in info.keys():
                uuid, creditor, debtor, cates = info[key][0],info[key][1],info[key][2],info[key][3]
                amount, deadline, period, ways = info[key][4],info[key][5],info[key][6],info[key][7]
                if_fwarnnt = info[key][8]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(assure_string,(gs_basic_id,gs_report_id, uuid, province, creditor, debtor, cates, amount, deadline, period, ways,if_fwarnnt, updated_time, updated_time))
                insert_flag += flag
                connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("report assure error:%s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark, total, insert_flag, update_flag