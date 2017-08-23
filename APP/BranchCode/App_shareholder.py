#!/usr/bin/env Python
#-*- coding:utf-8 -*-

import logging
import sys
import time
from PublicCode.Public_code import Judge_status
from PublicCode import deal_html_code
from PublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code, true_amount,reg_amount,ta_ways,ta_date,country,address,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'
update_share_py = 'update gs_py set gs_py_id = %s,gs_shareholder = %s,updated = %s where gs_py_id = %s'
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
                if single["blicTypeInterpreted"]=='':
                    license_code = None
                    license_type = None
                elif single["cetfTypeInterpreted"] =='':
                    license_type = None
                    license_code = None
                elif single["blicTypeInterpreted"]!='':
                    license_type = single["blicTypeInterpreted"]
                    license_code = single["bLicNo"]
                elif single["cetfTypeInterpreted"]:
                    license_type = single["cetfTypeInterpreted"]
                    license_code = single["cerNo"]
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
                    ta_date = None
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
                    address = None
                info[i] = [name,types,license_code,license_type,reg_amount,true_amount,ta_date,ta_ways,country,address]
        return info

    def update_to_db(self,cursor, connect,gs_basic_id, info):
        remark = 0
        cate = 0
        insert_flag,update_flag = 0,0
        total = len(info)
        logging.info("share total:%s"%total)
        try :
            for key in info.keys():
                name, types, license_code, license_type = info[key][0],info[key][1],info[key][2],info[key][3]
                reg_amount, true_amount, ta_date, ta_ways = info[key][4],info[key][5],info[key][6],info[key][7]
                country, address = info[key][8],info[key][9]
                count = cursor.execute(select_string, (gs_basic_id, name, types, cate))
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(share_string, (
                            gs_basic_id, name, cate, types, license_type, license_code, true_amount,
                            reg_amount, ta_ways, ta_date,country,address,updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception,e:
            remark = 100000006
            logging.error("shareholder error :%s"%e)
        finally:
            if remark < 100000001:
                if remark < 100000001:
                    remark = insert_flag
                    logging.info("execute share:%s"%remark)
            # print remark
            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().updaye_py(gs_py_id,gs_basic_id,Share,"shareholder",data,update_share_py)




