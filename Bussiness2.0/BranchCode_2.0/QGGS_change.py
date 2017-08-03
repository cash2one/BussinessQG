#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_change.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取变更信息，并进行更新


import datetime
import logging
import sys
import time
import re
from PublicCode.deal_html_code import deal_lable
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log
url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_py_id = sys.argv[3]

# url = 'http://www.gsxt.gov.cn/%7B5l_RJDt6qW3U2WQziG7diOKL_p66iUtxr0dE_cRGxi69ApBl5Te5Ek19T0msEk3BXQntVA9TfucXVo6JT_ejxNafS8E3_vtenmHnlvAO8SQQShlay6H7vjLuV_IrhoXw-1501664728692%7D'
# gs_basic_id = 229418502
# gs_py_id = 1501

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,updated)values(%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s '
update_change_py = 'update gs_py set gs_py_id = %s,gs_change = %s,updated = %s where gs_py_id = %s'

class Change:
    def name(self,data):
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


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag,update_flag = 0,0
        flag = 0
        try:
            for key in information.keys():
                content_before, content_after = information[key][0], information[key][1]
                change_date, item = information[key][2], information[key][3]
                types = '变更'
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                count = cursor.execute(select_string,(gs_basic_id,item,change_date))
                if count == 0:
                    row_count = cursor.execute(insert_string, (
                                gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
                    insert_flag += row_count
                    connect.commit()
                elif count > 1:
                    remark = 0
                    for gs_basic_id, content in cursor.fetchall():
                        if content == content_after:
                            remark = 1
                            break
                    if remark == 0:
                        row_count = cursor.execute(insert_string, (
                            gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
                        insert_flag += row_count
                        connect.commit()
        except Exception, e:
            flag = 100000006
            logging.error("change error :%s " % e)
        finally:
            if flag < 100000001:
                flag = insert_flag
            return flag,insert_flag,update_flag
def  main():
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    pages, perpages = 0,0
    urllist = url.split('||')
    Judge(gs_py_id, connect, cursor, gs_basic_id, urllist,pages,perpages).update_branch(update_change_py, Change, "change")
    cursor.close()
    connect.close()


if __name__ == "__main__":
    main()