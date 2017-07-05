#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

branch_string = 'insert into gs_branch(gs_basic_id,code,name,gov_dept,updated)values(%s,%s,%s,%s,%s)'
select_branch = 'select gs_branch_id from gs_branch where name = %s and code = %s and gs_basic_id = %s'

update_branch = 'update gs_branch set code = %s ,gov_dept = %s ,updated = %s where gs_branch_id = %s'


# url = 'http://www.gsxt.gov.cn/%7Bnr8WbMY0_DRNJ_Ku75MyX7rhJ3Pj28Re0meD5q9QvBjoIKK1Y5wEH9HRubJ2Nm0e3NsdWe-vtKon2zo1vTchFya1CNsp2ZQzRFjdSWwrPGA-1498184686833%7D'
# result = Send_Request.send_requests(url)
# data = json.loads(result)["data"]
def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        name = singledata["brName"]
        code = singledata["regNo"]
        uniscId = singledata["uniscId"]
        if uniscId !='':
            code = None
        gov_dept = singledata["regOrg_CN"]
        information[i] = [name, code, gov_dept]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        name = information[key][0]
        code = information[key][1]
        gov_dept = information[key][2]
        try:
            count = cursor.execute(select_branch, (name, code, gs_basic_id))
            if count == 0:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(branch_string, (gs_basic_id, code, name, gov_dept, updated_time))
                insert_flag += rows_count
                connect.commit()
            elif int(count) == 1:
                gs_branch_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(update_branch, (code, gov_dept, updated_time, gs_branch_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:
            logging.error("branch error:" % e)
    flag = insert_flag + update_flag
    return flag
