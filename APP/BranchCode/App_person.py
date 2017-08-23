#!/usr/bin/env Python
#-*- coding:utf-8 -*-

import sys
import time
import logging
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Log
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


select_string = 'select gs_person_id from gs_person where name = %s and position = %s and gs_basic_id = %s and source = 0'
insert_string = 'insert into gs_person(gs_basic_id,name,position,updated)values(%s,%s,%s,%s)'
person_string = 'update gs_person set gs_person_id = %s,updated = %s where gs_person_id = %s'
update_person_py = 'update gs_py set gs_py_id = %s,gs_person = %s,updated = %s where  gs_py_id = %s '
class Person:
    def name(self,data):
        info = {}
        if len(data)!=0:
            for i ,single in enumerate(data):
                name = single["personName"]
                if "positionInterpreted" in single.keys():
                    position = single["positionInterpreted"]
                else:
                    position = ''
                info[i] = [name,position]
        return info
    def update_to_db(self,cursor, connect,gs_basic_id, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        total = len(information)
        logging.info("person total:%s"%total)
        try:
            for key in information.keys():
                name = str(information[key][0])
                position = str(information[key][1])
                rows = cursor.execute(select_string, (name, position, gs_basic_id))
                # print name,position

                if int(rows) == 1:
                    pass
                elif rows == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    count = cursor.execute(insert_string, (gs_basic_id, name,position, updated_time))
                    insert_flag += count
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("person error: %s" % e)
        finally:
            if remark < 100000001:
                flag = insert_flag + update_flag
                remark = flag
                logging.info("execute person:%s"%remark)
            # print remark
            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    print_info = Judge_status().updaye_py(gs_py_id,gs_basic_id,Person,"person",data,update_person_py)
    return print_info







