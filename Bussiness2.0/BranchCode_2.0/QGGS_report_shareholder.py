#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_report_shareholder.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :年报股东及出资信息

#!/usr/bin/env python
# -*- coding:utf-8 -*-



import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
share_string = 'insert into gs_report_share(gs_basic_id,gs_report_id,province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,created,updated) values ' \
               '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Share:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            uuid = singledata["invId"]
            name = singledata["invName"]
            reg_amount = singledata["liSubConAm"]
            reg_date = singledata["subConDate"]
            reg_date = change_date_style(reg_date)
            reg_way = singledata["subConFormName"]
            ac_amount = singledata["liAcConAm"]
            ac_date = singledata["acConDate"]
            ac_date = change_date_style(ac_date)
            ac_way = singledata["acConForm_CN"]

            information[i] = [name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way]
        return information


    def update_to_db(self,gs_report_id, gs_basic_id, cursor, connect, information,province):
        insert_flag,update_flag = 0,0
        remark = 0
        try:
            for key in information.keys():
                name, uuid, reg_amount, reg_date = information[key][0], information[key][1], information[key][2], \
                                                  information[key][3]
                reg_way, ac_amount, ac_date, ac_way = information[key][4], information[key][5], information[key][6], \
                                                         information[key][7]

                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(share_string, (
                            gs_basic_id, gs_report_id,  province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,updated_time,updated_time))
                connect.commit()
                insert_flag += flag
        except Exception, e:
            remark = 100000001
            logging.error('share error %s' % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag
