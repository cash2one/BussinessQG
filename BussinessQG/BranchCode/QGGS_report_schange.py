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
schange_string = 'insert into gs_report_schange(gs_basic_id,id,gs_report_id,name,percent_pre,percent_after,dates,updated)values' \
                 '(%s,%s,%s,%s,%s,%s,%s,%s)'

select_schange = 'select gs_report_schange_id from gs_report_schange where gs_report_id = %s and name = %s '
update_schange = 'update gs_report_schange set percent_pre = %s ,percent_after = %s,dates = %s,updated = %s where gs_report_schange_id = %s'


def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["inv"]
        percent_pre = str(singledata["transAmPr"]) + '%'
        percent_after = str(singledata["transAmAft"]) + '%'
        dates = singledata["altDate"]
        dates = change_date_style(dates)
        information[i] = [name, percent_pre, percent_after, dates]
    return information


def update_to_db(gs_report_id, gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name, percent_pre, percent_after, dates = information[key][0], information[key][1], information[key][2], \
                                                  information[key][3]
        try:
            count = cursor.execute(select_schange, (gs_report_id, name))
            if count == 0:
                m = hashlib.md5()
                m.update(str(gs_basic_id) + str(gs_report_id) + '1')
                id = m.hexdigest()
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(schange_string, (
                gs_basic_id, id, gs_report_id, name, percent_pre, percent_after, dates, updated_time))
                connect.commit()
                insert_flag += flag
            elif int(count) == 1:
                gs_report_schange_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                flag = cursor.execute(update_schange,
                                      (percent_pre, percent_after, dates, updated_time, gs_report_schange_id))
                connect.commit()
                update_flag += flag
        except Exception, e:
            logging.error('schange error %s' % e)
    total = update_flag + insert_flag
    return total
