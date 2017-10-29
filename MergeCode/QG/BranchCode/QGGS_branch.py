#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_branch.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于获取分支机构信息并进行更新

import logging
import sys
import time
import hashlib
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.deal_html_code import remove_symbol

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

branch_string = 'insert into gs_branch(gs_basic_id,id,code,name,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_string = 'select * from gs_branch where id = %s and gs_basic_id =%s'

class Branch:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            name = singledata["brName"]
            code = singledata["regNo"]
            uniscId = singledata["uniscId"]
            # print uniscId
            if uniscId !='':
                code = ''
            gov_dept = singledata["regOrg_CN"]
            information[i] = [name, code, gov_dept]
        return information
    def update_to_db(self,gs_basic_id,information):
        insert_flag,update_flag = 0,0
        flag = 0
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                name = information[key][0]
                name = remove_symbol(name)
                code = information[key][1]
                gov_dept = information[key][2]
                m = hashlib.md5()
                m.update(str(gs_basic_id) + str(name))
                id = m.hexdigest()
                count = cursor.execute(select_string,(id, gs_basic_id))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(branch_string, (gs_basic_id,id, code, name, gov_dept, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            flag = 100000006
            logging.error('branch error: %s'%e)
        finally:
            cursor.close()
            connect.close()
            if flag < 100000001:
                flag = insert_flag
            return flag,insert_flag,update_flag
def main(gs_basic_id,url):
    Judge(gs_basic_id, url).update_branch(Branch, "branch")
