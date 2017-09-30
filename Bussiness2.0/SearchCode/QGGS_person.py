#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_person.py
# @Author: Lmm
# @Date  : 2017-08-08
# @Desc  :
import logging
import re
import sys
import time

from SPublicCode import config
from SPublicCode.deal_html_code import deal_lable
from SPublicCode.Public_code import Connect_to_DB
from SPublicCode.Judge_Status import Judge
from SPublicCode.Bulid_Log import Log
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_search_id = sys.argv[3]

# url = 'http://www.gsxt.gov.cn/%7Bh3PaFzrRehMR5SrwpBqrkAIrG4S4WWBAG2LE0hZDbzqRpa7_39xHUMFKuWLiWz-pSMDhKAptyNybj4wEFjwb0NwkCJduUfUXBke8_TDaXp6zCPJdxu3reoj_B6uk6VWqBJqCjOVXy2GOFi4D0KA4UA-1504578404397%7D'
# gs_basic_id = 1900000099
# gs_search_id = 837

select_string = 'select gs_person_id,position from gs_person where gs_basic_id = %s and name = %s and source = 1'
insert_string = 'insert into gs_person(gs_basic_id,name,position,source,updated)values(%s,%s,%s,%s,%s)'
person_string = 'update gs_person set gs_person_id = %s,position = %s,updated = %s,quit =0 where gs_person_id = %s'
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
            information[i] = [name, position]
        return information


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        
        try:
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
                rows = cursor.execute(select_string, (gs_basic_id,name))

                if int(rows) >= 1:
                    sign = 0
                    for gs_person_id,pos in cursor.fetchall():
                        if pos == position:
                            sign = 1
                            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                            count = cursor.execute(update_quit,(updated_time,gs_basic_id,gs_person_id))
                            connect.commit()
                            # update_flag+= count
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
            if remark < 100000001:
                flag = insert_flag + update_flag
                remark = flag
            return remark,insert_flag,update_flag
def main():
    Log().found_search_log(gs_search_id, gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    pages,perpages = 0,0
    Judge(connect,cursor,gs_basic_id,url,pages,perpages).update_branch(Person,"person")
    # cursor.close()
    # connect.close()

if __name__ =="__main__":
    main()