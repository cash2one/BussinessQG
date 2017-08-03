#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_clear.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取清算信息，并进行更新

import logging
import sys
import time
from PublicCode.deal_html_code import deal_lable
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_py_id = sys.argv[3]

# url = 'http://www.gsxt.gov.cn/%7B5l_RJDt6qW3U2WQziG7diOOfC3UC4PYR-fB3d0OCS7QhO96RLo49J9oGiL2HvR6h7z2_3RfhSpDYyi0SAslpirM_EsN25JdENt3uKuyHM7g4e3EAGAFqFhhCbx-MM5jI-1501664728707%7D'
# gs_basic_id = 229418502
# gs_py_id = 1501
insert_string = 'insert into gs_clear (gs_basic_id,person_name,positon,updated)values(%s,%s,%s,%s)'
select_string = 'select gs_clear_id from gs_clear where gs_basic_id = %s and person_name = %s and positon = %s'
update_string = 'update gs_clear set gs_clear_id = %s,updated = %s where gs_clear_id = %s'

update_clear_py = 'update gs_py set gs_py_id = %s,gs_clear = %s,updated = %s where gs_py_id = %s'

class Clear:
    def name(self,data):
        info = {}
        for i in xrange(len(data)):
            singledata = data[i]
            position = singledata["ligpriSign"]
            if position == "2":
                position = '清算组成员'
            elif position == "1":
                position = '清算组负责人'

            person_name = singledata["liqMem"]
            person_name = deal_lable(person_name)
            info[i] = [person_name,position]
        return info
    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        try:
            for key in information.keys():
                person_name = str(information[key][0])
                position = str(information[key][1])
                rows = cursor.execute(select_string, (person_name, position, gs_basic_id))
                if int(rows) == 1:
                    gs_clear_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    count = cursor.execute(update_string, (gs_clear_id,updated_time, gs_clear_id))
                    update_flag += count
                    connect.commit()
                elif rows == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    count = cursor.execute(insert_string, (gs_basic_id, person_name,position, updated_time))
                    insert_flag += count
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("clear error: %s" % e)
        finally:
            if remark < 100000001:
                flag = insert_flag + update_flag
                remark = flag
            return remark,insert_flag,update_flag

def main():
    Log().found_log(gs_py_id,gs_basic_id)
    pages,perpages = 0,0
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    Judge(gs_py_id,connect,cursor,gs_basic_id,url,pages,perpages).update_branch(update_clear_py,Clear,"clear")
    cursor.close()
    connect.close()
if __name__ =="__main__":
    main()
