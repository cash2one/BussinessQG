#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import sys
import time
from PublicCode.Public_code import Judge_status
from PublicCode import deal_html_code
from PublicCode.Public_code import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

stock_string = 'insert into gs_stock(gs_basic_id,equityno,pledgor,pled_blicno,impam,imporg,imporg_blicno,equlle_date,public_date,type,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_stock = 'select gs_stock_id from gs_stock where gs_basic_id = %s and equityNo = %s'
update_stock = 'update gs_stock set gs_basic_id = %s,pledgor = %s,pled_blicno = %s,impam = %s,imporg = %s,imporg_blicno = %s,equlle_date = %s,public_date = %s,type = %s ,updated = %s where gs_stock_id = %s'
update_stock_py = 'update gs_py set gs_py_id = %s,gs_stock = %s ,updated = %s where gs_py_id = %s'
class Stock:
    def name(self,data):
        information = {}
        for i in xrange(len(data)):
            singledata = data[i]
            if "pledgeNo" in singledata.keys():
                equityNo = singledata["pledgeNo"]
            else:
                equityNo = ''
            if "impAm" in singledata.keys():
                impAm = singledata["impAm"]
            else:
                impAm = ''
            if "impOrgName" in singledata.keys():
                impOrg = singledata["impOrgName"]
            else:
                impOrg = ''
            
            if "impBlicNo" in singledata.keys():
                impOrgBLicNo = singledata["impBlicNo"]
            else:
                impOrgBLicNo = ''
            # impOrgBLicType_CN = singledata["impOrgBLicType_CN"]
            # impOrgId = singledata["impOrgId"]
            # pledAmUnit = singledata["pledAmUnit"]
            if 'intBlicNo' in singledata.keys():
                pledBLicNo = singledata["intBlicNo"]
            else:
                pledBLicNo = ''
            # pledBLicType_CN = singledata["pledBLicType_CN"]
            if "intName" in singledata.keys():
                pledgor = singledata["intName"]
            else:
                pledgor = ''
            if "impTypeInterpreted" in singledata.keys():
                type = singledata["impTypeInterpreted"]
            else:
                type = ''
            if "equPleDate" in singledata.keys():
                equPleDate = singledata["equPleDate"]
                equPleDate = deal_html_code.change_chinese_date(equPleDate)
            else:
                equPleDate = None

            if "publicDate" in singledata.keys():
                publicDate = singledata["publicDate"]
            else:
                publicDate = None
            publicDate = deal_html_code.change_chinese_date(publicDate)
            information[i] = [equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type]
        return information


    def update_to_db( self,cursor, connect,gs_basic_id, information):
        insert_flag, update_flag = 0, 0
        remark = 0
        total = len(information)
        logging.info("stock total:%s"%total)
        try:
            for key in information.keys():
                equityNo, pledgor, pledBLicNo = information[key][0], information[key][1], information[key][2]
                impAm, impOrg, impOrgBLicNo = information[key][3], information[key][4], information[key][5]
                equPleDate, publicDate, type = information[key][6], information[key][7], information[key][8]

                count = cursor.execute(select_stock, (gs_basic_id, equityNo))
                    # print count
                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(stock_string, (
                        gs_basic_id, equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate, type,
                        updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif int(count) == 1:
                    gs_stock_id = cursor.fetchall()[0][0]
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

                    rows_count = cursor.execute(update_stock,
                                                    (gs_basic_id, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate,
                                                     publicDate, type, updated_time, gs_stock_id))
                    update_flag += rows_count
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("stock error: %s" % e)
        finally:
            flag = insert_flag + update_flag
            if remark < 100000001:
                remark = flag
                logging.info(" execute stock:%s"%remark)
            return remark,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data):
    Log().found_log(gs_py_id, gs_basic_id)
    Judge_status().updaye_py(gs_py_id,gs_basic_id,Stock,"stock",data,update_stock_py)
