#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
schange_string = 'insert into gs_report_schange(gs_basic_id,gs_report_id,province,name,percent_pre,percent_after,dates,uuid,created,updated)values' \
                 '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'



def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        uuid = singledata["anCheId"]
        name = singledata["inv"]
        percent_pre = str(singledata["transAmPr"]) + '%'
        percent_after = str(singledata["transAmAft"]) + '%'
        dates = singledata["altDate"]
        dates = change_date_style(dates)
        information[i] = [name, percent_pre, percent_after, dates,uuid]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information,province):
    insert_flag = 0
    remark = 0
    try:
        for key in information.keys():
            name, percent_pre, percent_after, dates = information[key][0], information[key][1], information[key][2], \
                                                      information[key][3]
            uuid = information[key][4]
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            flag = cursor.execute(schange_string, (
                    gs_basic_id, gs_report_id,province, name, percent_pre, percent_after, dates,uuid,updated_time, updated_time))
            connect.commit()
            insert_flag += flag

    except Exception, e:
        remark = 100000001
        logging.error('schange error %s' % e)
    finally:
        if remark < 100000001:
            remark = insert_flag
        # cursor.execute(schange_py,(remark,gs_basic_id))
        # connect.commit()

        return remark
