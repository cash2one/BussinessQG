#!/usr/bin/env Python
#!-*- coding:utf-8 -*-

from PublicCode import config
import sys
from PublicCode import deal_html_code
import time
import json
import logging
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Log
# 用于解决中文编码问题
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

update_string = 'update gs_basic set gs_basic_id = %s, name = %s ,ccode = %s,status = %s ,types = %s ,legal_person = %s, \
reg_date = %s ,appr_date = %s,reg_amount = %s, start_date = %s ,end_date = %s ,reg_zone = %s,reg_address = %s ,scope = %s ,del_date = %s,updated = %s where gs_basic_id = %s'
update_py = 'update gs_py set gs_py_id = %s,gs_basic = %s,updated = %s where gs_py_id = %s'
class Basic:
    def name(self,data):
        name = data["entName"]
        if "uniScid" in data.keys():
            ccode = data["uniScid"]
        else:
            ccode = ''
        if "opStateInterpreted" in data.keys():
            status = data["opStateInterpreted"]
        else:
            status = ''
        if "entTypeInterpreted" in data.keys():
            types = data["entTypeInterpreted"]
        else:
            types = ''
        if "lerep" in data.keys():
            legal_person = data["lerep"]
        else:
            legal_person = ''
        if "estDate" in data.keys():
            reg_date = data["estDate"]
            reg_date = deal_html_code.change_chinese_date(reg_date)
        else:
            reg_date = None
        if "issBlicDate"  in data.keys():
            appr_date = data["issBlicDate"]
            appr_date = deal_html_code.change_chinese_date(appr_date)
        else:
            appr_date = None
        if "regCapInterpreted" in data.keys():

            reg_amount = data["regCapInterpreted"]
        else:
            reg_amount = ''
        if "opFrom" in data.keys():
            start_date = data["opFrom"]
            start_date = deal_html_code.change_chinese_date(start_date)
        else:
            start_date = None

        if "opTo" in data.keys():
            end_date = data["opTo"]
            end_date = deal_html_code.change_chinese_date(end_date)
        else:
            end_date = None
        if "regOrganInterpreted" in data.keys():
            reg_zone = data["regOrganInterpreted"]
        else:
            reg_zone = ''
        if "dom" in data.keys():
            reg_address = data["dom"]
        else:
            reg_address = ''
        if "opScope" in data.keys():
            scope = data["opScope"]
            scope = deal_html_code.remove_symbol(scope)
        else:
            scope = ''
        if "canDate" in data.keys():
            del_date = data["canDate"]
            del_date = deal_html_code.change_chinese_date(del_date)
        else:
            del_date = None
        info = [name,ccode,status,types,legal_person,reg_date,appr_date,reg_amount,start_date,end_date,reg_zone,reg_address,scope,del_date]
        return info
    def update_to_db(self,cursor,connect,gs_basic_id,info):
        remark = 0
        try:
            name, ccode, status, types = info[0],info[1],info[2],info[3]
            legal_person, reg_date, appr_date, reg_amount = info[4],info[5],info[6],info[7]
            start_date, end_date, reg_zone, reg_address = info[8],info[9],info[10],info[11]
            scope, del_date = info[12],info[13]

            updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            row_count = cursor.execute(update_string,(gs_basic_id,name, ccode, status, types,legal_person, reg_date, appr_date, reg_amount,start_date, end_date, reg_zone, reg_address ,scope, del_date,updated_time,gs_basic_id))
            connect.commit()
        except Exception, e:
            logging.error("basic error:%s"%e)
            remark = 100000006
        finally:
            if remark <100000001:
                remark = row_count
                logging.info("update basic:%s"%remark)
            # print remark
            return remark
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    object = Basic()
    info = object.name(data)
    remark = object.update_to_db(cursor,connect,gs_basic_id,info)
    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    cursor.execute(update_py,(gs_py_id,remark,updated_time,gs_py_id))
    print 'basic:%s' % str(remark)
    cursor.close()
    connect.close()




