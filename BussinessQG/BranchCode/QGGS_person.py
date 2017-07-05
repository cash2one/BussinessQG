#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import re
import sys
import time

import config
from deal_html_code import deal_lable

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_string = 'select gs_person_id from gs_person where name = %s and position = %s and gs_basic_id = %s'
insert_string = 'insert into gs_person(gs_basic_id,name,position,updated)values(%s,%s,%s,%s)'
person_string = 'update gs_person set updated = %s where gs_person_id = %s'


def name(data):
    information = {}
    datalist = data
    for i in xrange(len(datalist)):
        data = datalist[i]
        name = data["name"]
        name = deal_lable(name)
        position = data["position_CN"]
        pattern = re.compile('.*img.*')
        key = re.findall(pattern, position)
        if len(key) != 0:
            position_key = config.person_img
            for key in position_key.keys():
                if key in position:
                    position = position_key[key]
                    break
        elif position != '':
            position = data["position_CN"]
        elif position == '':
            position = None
        information[i] = [name, position]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0

    for key in information.keys():
        name = str(information[key][0])
        position = str(information[key][1])
        rows = cursor.execute(select_string, (name, position, gs_basic_id))

        try:
            if int(rows) == 1:
                gs_person_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                count = cursor.execute(person_string, (updated_time, gs_person_id))
                update_flag += count
                connect.commit()
            elif rows == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                count = cursor.execute(insert_string, (gs_basic_id, name,position, updated_time))
                insert_flag += count
                connect.commit()
        except Exception, e:
            # print "person error:", e
            print e
            logging.error("person error: %s" % e)
    flag = insert_flag + update_flag
    # print insert_flag, update_flag
    # print flag
    return flag
