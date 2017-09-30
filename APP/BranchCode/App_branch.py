#!/usr/bin/env Python
#-*- coding:utf-8 -*-

import logging
import sys
import time
from PublicCode.Public_code import Judge_status
from PublicCode import deal_html_code
from PublicCode.Public_code import Log
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

#entBranchSet
branch_string = 'insert into gs_branch(gs_basic_id,id,code,name,gov_dept,ccode,updated)values(%s,%s,%s,%s,%s,%s,%s)'
select_branch = 'select gs_branch_id from gs_branch where gs_basic_id = %s and id = %s'
update_branch_py = 'update gs_py set gs_py_id= %s, gs_branch = %s,updated = %s where gs_py_id = %s'

class Branch:
    def name(self,data):
        info = {}
        if len(data)!=0:
            for i,single in enumerate(data):
                if "regNo" in single.keys():
                    code = single["regNo"]
                    code = deal_html_code.remove_symbol(code)
                else:
                    code = ''
                if "uniScid" in single.keys():
                    ccode = single["uniScid"]
                else:
                    ccode = ''
                ccode = deal_html_code.remove_symbol(ccode)
                if "brName" in single.keys():
                    name = single["brName"]
                    name = deal_html_code.remove_symbol(name)
                else:
                    name = ''
                if "regOrganName" in single.keys():
                    gov_dept = single["regOrganName"]
                    gov_dept = deal_html_code.remove_symbol(gov_dept)
                else:
                    gov_dept = ''
                info[i] = [name, code, gov_dept,ccode]
        return info
    def update_to_db(self,cursor, connect, gs_basic_id,information):
        insert_flag, update_flag = 0, 0
        flag = 0
        total = len(information)
        logging.info('branch total:%s'%total)
        try:
            for key in information.keys():
                name = information[key][0]
                code = information[key][1]
                gov_dept = information[key][2]
                ccode = information[key][3]
                m = hashlib.md5()
                m.update(str(gs_basic_id) + str(name))
                id = m.hexdigest()
                count = cursor.execute(select_branch,(gs_basic_id,id))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(branch_string, (gs_basic_id,id, code, name, gov_dept,ccode, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            flag = 100000006
            logging.error('branch error: %s' % e)
        finally:
            if flag < 100000001:
                flag = insert_flag+update_flag
                logging.info('execute branch %s'%flag)
            # print flag
            return flag,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().update_py(gs_py_id,gs_basic_id,Branch,"branch",data,update_branch_py)












