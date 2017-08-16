#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_permit.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :行政许可信息更新


import hashlib
import logging
import sys
import time
import re
from PublicCode.deal_html_code import change_date_style
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id = sys.argv[3]

url = 'http://www.gsxt.gov.cn/%7BT3MeYJuLFfLz3_3hCLfW_D7rl24ej0FREfGxNgxzT64_NUmxZAyzXCNptPDbN6CTpIP0K5DJ4gk9glIGRMPpacfPFH9-rhCmtSezoqOCtNk-1502787164569%7D'
gs_basic_id = 1900000103
gs_py_id = 1501
# http://www.gsxt.gov.cn/%7BdDJl9n7SHrdg23Xbla16SR9L3HDMcRaEl-7SHfBdMBBmJDWFHRdN2BkawosGi2dFRTlso9Njpd_ENzN-yHkIRKUuGQZhM5PG69aSmJuDixomEzjQC306yg-87wjE4wFI-1501740503025%7Dqisusohttp://www.gsxt.gov.cn/%7BdDJl9n7SHrdg23Xbla16SaS_FabCuuYFgn8OGRF2PRmJDWFHRdN2BkawosGi2dF03_xDEmHRZAg2aRhGXqhhxsuOXRtZXJfMjQLGA0O7oAVxMHpMgIa_45I9V09LXKBeFRrYTCawphBQDg_1k1T7w-1501737583814%7D

 # 204109602 1327

select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s and source = 1'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_permit_py = 'update gs_py set gs_py_id = %s ,gs_permit = %s ,updated = %s where gs_py_id = %s'

class Permit:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            name = singledata["entName"]
            code = singledata["licNo"]
            filename = singledata["licName_CN"]
            start_date = singledata["valFrom"]
            start_date = change_date_style(start_date)
            end_date = singledata["valTo"]
            end_date = change_date_style(end_date)
            content = singledata["licItem"]
            gov_dept = singledata["licAnth"]
            information[i] = [name, code, filename, start_date, end_date, content, gov_dept]
        return information


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag,update_flag = 0,0
        remark = 0
        source = 1
        for key in information.keys():
            name, code, filename, start_date = information[key][0], information[key][1], information[key][2], \
                                               information[key][3]
            end_date, content, gov_dept = information[key][4], information[key][5], information[key][6]
            count = cursor.execute(select_string, (gs_basic_id, filename,code,start_date,end_date))
            m = hashlib.md5()
            m.update(code)
            id = m.hexdigest()
            # print filename
            try:
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(permit_string, (
                        gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, source,updated_time))
                    insert_flag += rows_count
                    connect.commit()

            except Exception, e:
                remark = 100000006
                logging.error("permit error: %s" % e)
        if remark < 100000001:
            remark = insert_flag
        return remark,insert_flag,update_flag

def main():
    Log().found_log(gs_py_id,gs_basic_id)
    pages,perpages = 0,0
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    # urllist = url.split('qisuso')
    Judge(gs_py_id,connect,cursor,gs_basic_id,url,pages,perpages).update_branch(update_permit_py,Permit,"permit")
    cursor.close()
    connect.close()

if __name__ =="__main__":
    main()