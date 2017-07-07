#!/usr/bin/env python
# -*- coding:utf-8 -*-


import hashlib
import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
share_string = 'insert into gs_report_share(gs_basic_id,gs_report_id,province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,created,updated) values ' \
               '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_share = 'select gs_report_share_id from gs_report_share where gs_report_id = %s and name = %s'
update_share = 'update gs_report_share set reg_amount = %s, reg_date = %s, reg_way = %s, ac_amount = %s, ac_date = %s, ac_way = %s,updated = %s where gs_shareholder_id = %s'


def name(data):
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
        ac_date= change_date_style(ac_date)
        ac_way = singledata["acConForm_CN"]
        information[i] = [name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information,province):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name, uuid, reg_amount, reg_date = information[key][0], information[key][1], information[key][2], \
                                          information[key][3]
        reg_way, ac_amount, ac_date, ac_way = information[key][4], information[key][5], information[key][6], \
                                                 information[key][7]
        try:
            count = cursor.execute(select_share, (gs_report_id, name))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(share_string, (
                    gs_basic_id, gs_report_id,  province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,updated_time,updated_time))
                connect.commit()
                insert_flag += flag
            elif int(count) == 1:
                gs_shareholder_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_share, (
                    reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way, updated_time, gs_shareholder_id))
                connect.commit()
                update_flag += flag
        except Exception, e:
            logging.error('share error %s' % e)
    total = update_flag + insert_flag
    return total
