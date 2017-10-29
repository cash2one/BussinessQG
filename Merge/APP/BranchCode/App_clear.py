#!/usr/bin/env Python
#-*- coding:utf-8 -*-

import logging
import sys
import time
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Judge_status
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

insert_string = 'insert into gs_clear (gs_basic_id,person_name,positon,updated)values(%s,%s,%s,%s)'
select_string = 'select gs_clear_id from gs_clear where gs_basic_id = %s and person_name = %s and positon = %s'
update_string = 'update gs_clear set gs_clear_id = %s,updated = %s where gs_clear_id = %s'

class Clear:
    def name(self,data):
        info = {}
        for i,singledata in enumerate(data):
            position = singledata["position"]
            if position == "02":
                position = '清算组成员'
            elif position == "01":
                position = '清算组负责人'

            person_name = singledata["personName"]
            info[i] = [person_name,position]
        return info
    def update_to_db(self,gs_basic_id, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        total = len(information)
        logging.info("clear error:%s"%total)
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                person_name = str(information[key][0])
                position = str(information[key][1])
                rows = cursor.execute(select_string, (gs_basic_id,person_name, position))
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
            cursor.close()
            connect.close()
            if remark < 100000001:
                flag = insert_flag + update_flag
                logging.info("execute clear:%s"%flag)
                remark = flag
            return remark,total,insert_flag,update_flag
def main(gs_basic_id,data):
  
    print_info = Judge_status().update_info(gs_basic_id,Clear,"clear",data)
    return print_info
