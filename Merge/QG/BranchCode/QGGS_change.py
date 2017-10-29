#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_change.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取变更信息，并进行更新

import logging
import sys
import time
from PublicCode.deal_html_code import deal_lable
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode import deal_html_code


reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s and source =1 '


class Change:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            single_data = data[i]
            content_before = single_data["altBe"]
            content_after = single_data["altAf"]
            change_date = single_data["altDate"]
            change_date = deal_html_code.change_date_style(change_date)
            item = single_data["altItem_CN"]
            item = deal_lable(item)
            information[i] = [content_before, content_after, change_date, item]
        return information


    def update_to_db(self,gs_basic_id, information):
        insert_flag,update_flag = 0,0
        flag = 0
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                content_before, content_after = information[key][0], information[key][1]
                change_date, item = information[key][2], information[key][3]
                types = '变更'
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                count = cursor.execute(select_string,(gs_basic_id,item,change_date))
                if count == 0:
                    source = 1
                    row_count = cursor.execute(insert_string, (
                                gs_basic_id, types, item, content_before, content_after, change_date,source,updated_time))
                    insert_flag += row_count
                    connect.commit()
                elif count >= 1:
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
            cursor.close()
            connect.close()
            if flag < 100000001:
                flag = insert_flag
            return flag,insert_flag,update_flag
def main(gs_basic_id,url):
    Judge(gs_basic_id, url).update_branch(Change, "change")
