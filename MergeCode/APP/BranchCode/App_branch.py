#!/usr/bin/env Python
#-*- coding:utf-8 -*-

import hashlib
import logging
import sys
import time

from PublicCode import config
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Connect_to_DB

from PublicCode import deal_html_code

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

#entBranchSet
branch_string = 'insert into gs_branch(gs_basic_id,id,code,name,gov_dept,ccode,updated)values(%s,%s,%s,%s,%s,%s,%s)'
select_branch = 'select gs_branch_id from gs_branch where gs_basic_id = %s and id = %s'


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
    def update_to_db(self, gs_basic_id,information):
        
        insert_flag, update_flag = 0, 0
        flag = 0
        total = len(information)
        logging.info('branch total:%s'%total)
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
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
                    rows_count = cursor.execute(branch_string, (gs_basic_id, id,code, name, gov_dept,ccode, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            flag = 100000006
            logging.error('branch error: %s' % e)
        finally:
            cursor.close()
            connect.close()
            if flag < 100000001:
                flag = insert_flag+update_flag
                logging.info('execute branch %s'%flag)
            # print flag
            return flag,total,insert_flag,update_flag
def main(gs_basic_id,data):
    Judge_status().update_info(gs_basic_id,Branch,"branch",data)












