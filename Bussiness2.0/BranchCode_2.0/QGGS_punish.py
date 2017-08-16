#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_punish.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :行政处罚信息

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style
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

# url = config.host+'/%7BqNZNxK-tltgvV_n1dcLOp6hfe47auXppVC4Rd8axnwGaKWhIJ9xBbthFPhMc8AQ_VISMUgl3nt3CdO2rIAeE8MuQ8dqmLHgcha7VzIsxGNcHIhAl5bqKXujUAQ12wF3Y-1502688815142%7D'
# gs_basic_id = 1900000098
# gs_py_id = 1501
punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,name,pdfurl,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'
update_punish_py = 'update gs_py set gs_py_id = %s, gs_punish = %s ,updated = %s where gs_py_id = %s'

class Punish:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            number = singledata["penDecNo"]
            types = singledata["illegActType"]
            content = singledata["penContent"]
            date = singledata["penDecIssDate"]
            date = change_date_style(date)
            pub_date = singledata["publicDate"]
            pub_date = change_date_style(pub_date)
            gov_dept = singledata["penAuth_CN"]
            nodeNum = singledata["nodeNum"]
            name = singledata["unitName"]
            vPunishmentDecision = singledata["vPunishmentDecision"]
            if len(vPunishmentDecision)==0:
                pdfurl = None
            else:
                fileName = vPunishmentDecision["fileName"]
                pdfurl = config.host+'/doc/%s/casefiles/'%nodeNum+fileName
                # print pdfurl
            information[i] = [number, types, content, date, pub_date, gov_dept,name,pdfurl]
        return information

    def update_to_db(self,gs_basic_id, cursor, connect, information):
        insert_flag,update_flag = 0,0
        remark = 0

        try:
            for key in information.keys():
                number, types, content = information[key][0], information[key][1], information[key][2]
                date, pub_date, gov_dept = information[key][3], information[key][4], information[key][5]
                name,pdfurl = information[key][6],information[key][7]
                count = cursor.execute(select_punish, (gs_basic_id, number))
                if count == 0:
                    m = hashlib.md5()
                    m.update(str(number))
                    id = m.hexdigest()
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(punish_string, (
                        gs_basic_id, id, number, types, content, date, pub_date, gov_dept,name,pdfurl, updated_time))
                    insert_flag += rows_count
                    connect.commit()

        except Exception, e:
            remark = 100000006
            logging.error("punish error:%s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag
def main():
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    pages, perpages = 0, 0
    Judge(gs_py_id,connect,cursor,gs_basic_id,url,pages,perpages).update_branch(update_punish_py,Punish,"punish")
    cursor.close()
    connect.close()


if __name__ =="__main__":
    main()