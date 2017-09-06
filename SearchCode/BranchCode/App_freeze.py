#!/usr/bin/env python
# -*- coding:utf-8 -*-


import json
import logging
import sys
import time
from SPublicCode import config
from SPublicCode.Public_code import Connect_to_DB
from SPublicCode.Public_code import Log
from SPublicCode import deal_html_code
from SPublicCode.Public_code import Judge_status
import requests

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
freeze_string = 'insert into gs_freeze(gs_basic_id,executor, stock_amount, court, notice_no,status,items, rule_no, enforce_no,cert_cate,cert_code, start_date, end_date,period, pub_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_freeze = 'select gs_freeze_id from gs_freeze where gs_basic_id = %s and rule_no = %s'

freeze_list = {
    'SHH':'http://sh.gsxt.gov.cn/notice/ws/data/ent_stockfreeze/{0}',
    'HEB':"http://he.gsxt.gov.cn/notice/ws/data/ent_stockfreeze/{0}",
    'SCH':'http://sc.gsxt.gov.cn/notice/ws/data/ent_stockfreeze/{0}',
    'YUN':'http://yn.gsxt.gov.cn/notice/ws/data/ent_stockfreeze/{0}'

}
class Freeze:
    def name(self,data,province):
        information = {}
        for i,singledata in enumerate(data):
            if "inv" in singledata.keys():
                executor = singledata["inv"]
            else:
                executor = ''
            if "regCapInterpreted" in singledata.keys():
                stock_amount = singledata["regCapInterpreted"]
            else:
                stock_amount = ''
            if "froAuth" in singledata.keys():
                court = singledata["froAuth"]
            else:
                court = ''
            if "executeNo" in singledata.keys():
                notice_no = singledata["executeNo"]
            else:
                notice_no = ''
            if "frozStateInterpreted" in singledata.keys():
                status = singledata["frozStateInterpreted"]
            else:
                status = ''
            stockFreezeId = singledata["stockFreezeId"]
            detail_url = freeze_list[province].format(stockFreezeId)
            items, rule_no, enforce_no, cert_cate, cert_code, start_date, end_date, period, pub_date = self.deal_detail_content(
                    detail_url)
            information[i] = [executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no, cert_cate,
                              cert_code, start_date, end_date, period, pub_date]
        return information

    #用于处理详情页，获取详情页信息
    def deal_detail_content(self,detail_url):
        result= requests.get(detail_url)
        status_code = result.status_code
        result = result.content
        if status_code == 200:
           if len(result)!=0:
                data = json.loads(result)["entBlackList"][0]
                if "executeItemInterpreted" in data.keys():
                    items = data["executeItemInterpreted"]
                else:
                    items = ''
                if "froDocNo" not in data.keys():
                    rule_no = data["executeNo"]
                elif "executeNo" in data.keys():
                    rule_no = data["froDocNo"]
                else:
                    rule_no = ''
                if "executeNo" in data.keys():
                    enforce_no = data["executeNo"]
                else:
                    enforce_no = ''
                if "cerType" in data.keys():
                    cert_cate = data["cetfTypeInterpreted"]
                    cert_code = data["cerNo"]
                elif "blicType" in data.keys():
                    cert_cate = data["blicTypeInterpreted"]
                    cert_code = data["blicNo"]
                if "froFrom" in data.keys():
                    start_date = data["froFrom"]
                    start_date = deal_html_code.change_chinese_date(start_date)
                else:
                    start_date = None
                if "froTo" in data.keys():
                    end_date = data["froTo"]
                    end_date = deal_html_code.change_chinese_date(end_date)
                else:
                    end_date = None
                if "frozDeadline" in data.keys():
                    period = data["frozDeadline"]
                else:
                    period = None
                if "publicDate" in data.keys():
                    pub_date = data["publicDate"]
                    pub_date = deal_html_code.change_chinese_date(pub_date)
                else:
                    pub_date = None


        return items, rule_no, enforce_no, cert_cate, cert_code, start_date, end_date, period, pub_date


    def update_to_db(self,cursor, connect,gs_basic_id, information):
        insert_flag,update_flag= 0,0
        flag = 0
        total = len(information)
        try:
            for key in information.keys():
                executor, stock_amount, court, notice_no = information[key][0], information[key][1], information[key][2], \
                                                           information[key][3]
                status, items, rule_no, enforce_no = information[key][4], information[key][5], information[key][6], \
                                                     information[key][7]
                cert_cate, cert_code, start_date, end_date = information[key][8], information[key][9], information[key][10], \
                                                             information[key][11]
                period, pub_date = information[key][12], information[key][13]

                count = cursor.execute(select_freeze, (gs_basic_id, rule_no))
                if count == 0:

                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(freeze_string, (
                    gs_basic_id, executor, stock_amount, court, notice_no, status, items, rule_no, enforce_no,
                    cert_cate, cert_code, start_date, end_date, period, pub_date, updated_time))
                    insert_flag += rows_count
                    connect.commit()
        except Exception, e:
            logging.error("freeze error: %s" % e)
            flag = 100000006
        finally:
            if flag <100000001:
                flag = insert_flag
            return flag,total,insert_flag,update_flag
def main(gs_py_id,gs_basic_id,data,province):
    Log().found_log(gs_py_id, gs_basic_id)
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        info = Freeze().name(data,province)
        flag, total, insert_flag, update_flag = Freeze().update_to_db(cursor,connect,gs_basic_id,info)
        flag = Judge_status().judge(flag,total)
        string = 'freeze:' + str(flag) + '||' + str(total) + '||' + str(insert_flag) + '||' + str(update_flag)
        print string

    except Exception,e:
        logging.error("freeze error :%s"%e)
    finally:
        cursor.close()
        connect.close()

