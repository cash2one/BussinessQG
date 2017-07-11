#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import logging
import sys
import time

from PublicCode.deal_html_code import deal_lable

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

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
    insert_flag = 0
    flag = 0
    try:
        for key in information.keys():
            content_before, content_after = information[key][0], information[key][1]
            change_date, item = information[key][2], information[key][3]
            types = '变更'
            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            row_count = cursor.execute(insert_string, (
                        gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
            insert_flag += row_count
            connect.commit()
    except Exception, e:
        flag = 100000001
        logging.error("change error :%s " % e)
    finally:
        if flag < 100000001:
            flag = insert_flag
        return flag
