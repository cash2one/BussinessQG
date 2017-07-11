#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

branch_string = 'insert ignore into gs_branch(gs_basic_id,code,name,gov_dept,updated)values(%s,%s,%s,%s,%s)'
select_string = 'select * from gs_branch where name = %s and gs_basic_id = %s'
def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["brName"]
        code = singledata["regNo"]
        uniscId = singledata["uniscId"]
        # print uniscId
        if uniscId !='':
            code = None
        gov_dept = singledata["regOrg_CN"]
        information[i] = [name, code, gov_dept]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag = 0
    flag = 0
    try:
        for key in information.keys():
            name = information[key][0]
            code = information[key][1]
            gov_dept = information[key][2]

            count = cursor.execute(select_string,(name, gs_basic_id))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(branch_string, (gs_basic_id, code, name, gov_dept, updated_time))
                insert_flag += rows_count
                connect.commit()

    except Exception, e:
        flag = 100000001
        logging.error('branch error: %s'%e)
    finally:
        if flag <100000001:
            flag = insert_flag
        return flag

