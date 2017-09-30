#!/usr/bin/env Python
#-*- coding:utf-8 -*-

import logging
import sys
import time
from PublicCode import config
from PublicCode.Public_code import Judge_status
from PublicCode import deal_html_code
from PublicCode.Public_code import Log
from PublicCode.Public_code import Connect_to_DB
import re
import base64
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

update_share_py = 'update gs_py set gs_py_id = %s,gs_shareholder = %s,updated = %s where gs_py_id = %s'
share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code, true_amount,reg_amount,ta_ways,ta_date,country,address,iv_basic_id,ps_basic_id,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'
select_name = 'select gs_basic_id from gs_unique where name = "%s"'
select_ps = 'select ps_basic_id,gs_basic_id from ps_basic where name = "%s"'
insert_ps = 'insert into ps_basic(gs_basic_id,name,idcard,province,city,town,birthday,encode,remark,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_ps = 'update ps_basic set ps_basic_id = %s ,gs_basic_id = %s,updated = %s where ps_basic_id = %s'
update_share = 'update gs_shareholder set quit = 1 where gs_basic_id = %s and cate = 0'
update_quit = 'update gs_shareholder set quit = 0,updated = %s where gs_shareholder_id = %s and gs_basic_id = %s'
class Share:
    def name(self,data):
        info = {}
        if len(data)!=0:
            for i,single in enumerate(data):
                if "invName" in single.keys():
                    name = single["invName"]
                else:
                    name = ''
                if "invTypeInterpreted" in single.keys():
                    types = single["invTypeInterpreted"]
                else:
                    types = ''
                if single["blicTypeInterpreted"]!='':
                    license_type = single["blicTypeInterpreted"]
                    license_code = single["bLicNo"]
                elif single["cetfTypeInterpreted"]!='':
                    license_type = single["cetfTypeInterpreted"]
                    license_code = single["cetfId"]
                elif single["blicTypeInterpreted"]=='' and single["cetfTypeInterpreted"] =='':
                    license_code = ''
                    license_type = ''
                license_code = deal_html_code.remove_symbol(license_code)
                if "subconAm" in single.keys():
                    reg_amount = single["subconAm"]
                else:
                    reg_amount = ''
                if "acconAm" in single.keys():
                    true_amount = single["acconAm"]
                else:
                    true_amount = ''
                if "conDate" in single.keys():
                    ta_date = single["conDate"]
                    ta_date = deal_html_code.change_chinese_date(ta_date)
                else:
                    ta_date = '0000-00-00'
                if "conForm" in single.keys():
                    ta_ways = single["conForm"]
                else:
                    ta_ways = ''
                if ta_ways == '1':
                    ta_ways = '货币'
                if "countryInterpreted" in single.keys():
                    country = single["countryInterpreted"]
                else:
                    country = ''
                if "dom" in single.keys():
                    address = single["dom"]
                else:
                    address = ''
                encrypted = single["encrypted"]
                cetfType = single["cetfType"]
                info[i] = [name, types, license_code, license_type, reg_amount, true_amount, ta_date, ta_ways, country,
                           address, encrypted, cetfType]
        return info
    def judge_certcode(self,name,code,cursor,connect,basic_id):
        ps = 0
        if len(code)== 15 or len(code)==18:
            select_string = select_ps %name
            count = cursor.execute(select_string)
            if int(count)==1:
                for ps_basic_id,gs_basic_id in cursor.fetchall():
                    if basic_id in gs_basic_id:
                        ps = ps_basic_id
                    else:
                        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        gs_basic_id = gs_basic_id+'"'+str(basic_id)+'",'
                        cursor.execute(update_ps,(ps_basic_id,gs_basic_id,updated_time,ps_basic_id))
                        connect.commit()
                        ps = ps_basic_id
            elif int(count) ==0 :
                idcard = code
                province = code[0:2]
                city = code[2:4]
                town = code[4:6]
                if len(code)==15:
                    birthday= code[6:12]
                elif len(code)==18:
                    birthday = code[6:14]
                if len(code)==15:
                    encode = base64.b64encode(code[12:15])
                elif len(code)==18:
                    encode = base64.b64encode(code[14:18])
                gs_basic_id = '"'+str(basic_id)+'",'
                remark = ''
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(insert_ps,(gs_basic_id,name,idcard,province,city,town,birthday,encode,remark,updated_time,updated_time))
                ps = connect.insert_id()
                connect.commit()
            return ps
    def update_to_db(self,cursor, connect,gs_basic_id, info):
        remark = 0
        cate = 0
        insert_flag,update_flag = 0,0
        total = len(info)
        logging.info("share total:%s"%total)
        try:
            string = update_share % gs_basic_id
            cursor.execute(string)
            connect.commit()
            cursor.close()
            connect.close()
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in info.keys():
                name, types, license_code, license_type = info[key][0],info[key][1],info[key][2],info[key][3]
                reg_amount, true_amount, ta_date, ta_ways = info[key][4],info[key][5],info[key][6],info[key][7]
                country, address = info[key][8],info[key][9]
                if name!= '' :
                    pattern = re.compile('.*公司.*|.*中心.*|.*集团.*|.*企业.*')
                    result = re.findall(pattern,name)
                    if len(result) ==0:
                        iv_basic_id = 0
                    else:
                        select_unique = select_name % name
                        number=cursor.execute(select_unique)
                        if number ==0:
                            iv_basic_id = 0
                        elif int(number)==1:
                            iv_basic_id = cursor.fechall[0][0]
                else:
                    iv_basic_id = 0

                encrypted = info[key][10]
                cetfType = info[key][11]
                ps_basic_id = 0
                if cetfType == '1':
                    if license_code == '' or license_code == '':
                        license_code = '非公示项'
                    
                    elif len(license_code) == 15 or len(license_code) == 18:
                        ps_basic_id = self.judge_certcode(name, license_code, cursor, connect, gs_basic_id)
                elif encrypted == '0':
                    license_code = '非公示项'
                count = cursor.execute(select_string, (gs_basic_id, name, types, cate))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(share_string, (
                            gs_basic_id, name, cate, types, license_type, license_code, true_amount,
                            reg_amount, ta_ways, ta_date,country,address,iv_basic_id,ps_basic_id,updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif int(count) == 1:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    gs_shareholder_id = cursor.fetchall()[0][0]
                    cursor.execute(update_quit, (updated_time, gs_shareholder_id, gs_basic_id))
                    connect.commit()

        except Exception,e:
            # print e
            remark = 100000006
            logging.error("shareholder error :%s"%e)
        finally:
            cursor.close()
            connect.close()
            if remark < 100000001:
                remark = insert_flag
                logging.info("execute share:%s"%remark)
            # print remark
            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().update_py(gs_py_id,gs_basic_id,Share,"shareholder",data,update_share_py)




