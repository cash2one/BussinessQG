#!/usr/bin/env Python
# -*- coding:utf-8 -*-

import logging
import sys
import time

from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status

from PublicCode import deal_html_code

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s and source =0 '


class Change:

    def name(self,data):
        info = {}
        if len(data)>0:
            for i,single in enumerate(data):
                if "altBe" in single.keys():
                    content_before = single["altBe"]
                else:
                    content_before = ''
                if "altAf" in single.keys():
                    content_after = single["altAf"]
                else:
                    content_after = ''
                if "altDate" in single.keys():
                    change_date = single["altDate"]
                    change_date = deal_html_code.change_chinese_date(change_date)
                else:
                    change_date = '0000-00-00'
                if "altItem" in single.keys():
                    item = single["altItem"]
                else:
                    item = ""
                info[i] = [content_before, content_after, change_date, item]
        return info
    def update_to_db(self,gs_basic_id,information):
        insert_flag,update_flag= 0,0
        flag = 0
        total = len(information)
        logging.info('change total:%s'%total)
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                content_before, content_after = information[key][0], information[key][1]
                change_date, item = information[key][2], information[key][3]
                types = '变更'
                source = 0
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                count = cursor.execute(select_string, (gs_basic_id, item, change_date))
                if count == 0:

                    row_count = cursor.execute(insert_string, (
                        gs_basic_id, types, item, content_before, content_after, change_date, source, updated_time))
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
                            gs_basic_id, types, item, content_before, content_after, change_date, source,updated_time))
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
                logging.info('execute change:%s'%flag)
            return flag,total,insert_flag,update_flag
def main(gs_basic_id,data):
   
    Judge_status().update_info(gs_basic_id,Change,"change",data)
