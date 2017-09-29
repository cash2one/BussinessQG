#!/usr/bin/env Python
# -*- coding:utf-8 -*-

import logging
import sys
import time
from SPublicCode.Public_code import Judge_status
from SPublicCode import deal_html_code
from SPublicCode.Public_code import Log

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
                    change_date = None
                if "altItem" in single.keys():
                    item = single["altItem"]
                else:
                    item = ""
                info[i] = [content_before, content_after, change_date, item]
        return info
    def update_to_db(self,cursor, connect, gs_basic_id,information):
        insert_flag,update_flag= 0,0
        flag = 0
        total = len(information)
        logging.info('change total:%s'%total)
        try:
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
            if flag < 100000001:
                flag = insert_flag
                logging.info('execute change:%s'%flag)
            return flag,total,insert_flag,update_flag
def main(gs_search_id,gs_basic_id,data):
    Log().found_log(gs_search_id, gs_basic_id)
    Judge_status().update_py(gs_basic_id,Change,"change",data)
