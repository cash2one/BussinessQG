#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import logging
import sys
import time

from deal_html_code import deal_lable

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
select_string = 'select gs_change_id from gs_change where item = %s and change_date = %s and content_after = %s and gs_basic_id = %s'
change_string = 'update gs_change set types = %s, content_before = %s ,content_after = %s,updated = %s where gs_change_id = %s '
insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,updated)values(%s,%s,%s,%s,%s,%s,%s)'


def name(data):
    information = {}
    for i in xrange(len(data)):
        single_data = data[i]
        content_before = single_data["altBe"]
        content_after = single_data["altAf"]
        change_date = single_data["altDate"]
        change_date = datetime.datetime.utcfromtimestamp(change_date / 1000)
        otherStyleTime = change_date.strftime("%Y-%m-%d")
        change_date = otherStyleTime
        item = single_data["altItem_CN"]
        item = deal_lable(item)
        information[i] = [content_before, content_after, change_date, item]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        content_before, content_after = information[key][0], information[key][1]
        change_date, item = information[key][2], information[key][3]
        types = '变更'
        count = cursor.execute(select_string, (item, change_date, content_after, gs_basic_id))

        try:
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                row_count = cursor.execute(insert_string, (
                    gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
                insert_flag += row_count
                connect.commit()
            elif int(count) == 1:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                gs_change_id = cursor.fetchall()[0][0]
                row_count = cursor.execute(change_string,
                                           (types, content_before, content_after, updated_time, gs_change_id))
                update_flag += row_count
                connect.commit()
        except Exception, e:
            # print "change error:",e
            logging.error("change error:" % e)
    flag = insert_flag + update_flag
    # print insert_flag, update_flag
    # print flag
    return flag
