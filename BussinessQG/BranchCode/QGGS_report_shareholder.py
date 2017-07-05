import datetime
import hashlib
import json
import logging
import sys
import time

import QGGS_Report
from  PublicCode.Public_code import Send_Request as Send_Request
from deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
share_string = 'insert into gs_shareholder(gs_basic_id,gs_report_id,id,name,cate,reg_amount,ra_date,ra_ways,true_amount,ta_date,ta_ways,updated) values ' \
               '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_share = 'select gs_shareholder_id from gs_shareholder where gs_report_id = %s and name = %s'
update_share = 'update gs_shareholder set reg_amount = %s, ra_date = %s ,ra_ways = %s ,true_amount = %s ,ta_date = %s,ta_ways = %s ,updated = %s where gs_shareholder_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["invName"]
        cate = 1
        reg_amount = singledata["liSubConAm"]
        ra_date = singledata["subConDate"]
        ra_date = change_date_style(ra_date)
        ra_ways = singledata["subConFormName"]
        true_amount = singledata["liAcConAm"]
        ta_date = singledata["acConDate"]
        ta_date = change_date_style(ta_date)
        ta_ways = singledata["acConForm_CN"]
        information[i] = [name, cate, reg_amount, ra_date, ra_ways, true_amount, ta_date, ta_ways]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name, cate, reg_amount, ra_date = information[key][0], information[key][1], information[key][2], \
                                          information[key][3]
        ra_ways, true_amount, ta_date, ta_ways = information[key][4], information[key][5], information[key][6], \
                                                 information[key][7]
        try:
            count = cursor.execute(select_share, (gs_report_id, name))
            if count == 0:
                m = hashlib.md5()
                m.update(str(gs_basic_id) + str(gs_report_id) + '1')
                id = m.hexdigest()
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(share_string, (
                    gs_basic_id, gs_report_id, id, name, cate, reg_amount, ra_date, ra_ways, true_amount, ta_date,
                    ta_ways, updated_time))
                connect.commit()
                insert_flag += flag
            elif int(count) == 1:
                gs_shareholder_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_share, (
                    reg_amount, ra_date, ra_ways, true_amount, ta_date, ta_ways, updated_time, gs_shareholder_id))
                connect.commit()
                update_flag += flag
        except Exception, e:
            logging.error('share error %s' % e)
    total = update_flag + insert_flag
    return total
