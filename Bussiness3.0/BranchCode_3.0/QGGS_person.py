#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_person.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :人员信息的更新

import logging
import re
import sys
import time

from PublicCode import config
from PublicCode.deal_html_code import deal_lable
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



select_string = 'select gs_person_id,position from gs_person where gs_basic_id = %s and name = %s and source = 1'
insert_string = 'insert into gs_person(gs_basic_id,name,position,source,updated)values(%s,%s,%s,%s,%s)'
person_string = 'update gs_person set gs_person_id = %s,position = %s,updated = %s,quit =0 where gs_person_id = %s'
update_person_py = 'update gs_py set gs_py_id = %s,gs_person = %s,updated = %s where  gs_py_id = %s '
update_string = 'update gs_person set quit = 1 where gs_basic_id = %s '
update_quit = 'update gs_person set quit = 0,updated = %s where gs_basic_id = %s and gs_person_id = %s'
class Person:
    def name(self,data):
        information = {}
        datalist = data
        for i in xrange(len(datalist)):
            data = datalist[i]
            name = data["name"]
            name = deal_lable(name)
            position = data["position_CN"]
            pattern = re.compile('.*img.*')
            key = re.findall(pattern, position)
            if len(key) != 0:
                position_key = config.person_img
                for key in position_key.keys():
                    if key in position:
                        position = position_key[key]
                        break
            elif position != '':
                position = data["position_CN"].replace(" ","")
            elif position == '':
                position = ''
            #print name,position
            information[i] = [name, position]
        return information


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            string = update_string % gs_basic_id
            cursor.execute(string)
            connect.commit()
            cursor.close()
            connect.close()
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                name = str(information[key][0])
                position = information[key][1]
                rows = cursor.execute(select_string, ( gs_basic_id,name))
                # print name,position

                if int(rows) >= 1:
                    # gs_person_id = cursor.fetchall()[0][0]
                    sign = 0
                    for gs_person_id,pos in cursor.fetchall():
                        if pos == position:
                            sign = 1
                            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                            count = cursor.execute(update_quit, (updated_time, gs_basic_id, gs_person_id))
                            connect.commit()
                            # update_flag += count
                        elif pos == None and position != None:
                            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                            count = cursor.execute(person_string, (gs_person_id, position, updated_time, gs_person_id))
                            update_flag += count
                            connect.commit()
                            sign = 0
                    if sign == 0:
                        source = 1
                        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        count = cursor.execute(insert_string, (gs_basic_id, name, position, source, updated_time))
                        insert_flag += count
                        connect.commit()
                    else:
                        pass
                elif rows == 0:
                    source = 1
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    count = cursor.execute(insert_string, (gs_basic_id, name,position,source, updated_time))
                    insert_flag += count
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("person error: %s" % e)
        finally:
            cursor.close()
            connect.close()
            if remark < 100000001:
                flag = insert_flag + update_flag
                remark = flag
            return remark,insert_flag,update_flag
def main():
   
    # HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    # connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    connect,cursor = None,None
    pages,perpages = 0,0
    Judge(gs_py_id,connect,cursor,gs_basic_id,url,pages,perpages).update_branch(update_person_py,Person,"person")
    # cursor.close()
    # connect.close()

if __name__ =="__main__":
    main()