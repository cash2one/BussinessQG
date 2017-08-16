#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_shareholder.py
# @Author: Lmm
# @Date  : 2017-08-08
# @Desc  :
import json
import logging
import sys
import time

from  SPublicCode.Public_code import Send_Request as Send_Request
from SPublicCode.deal_html_code import change_date_style
from SPublicCode.deal_html_code import deal_lable
from SPublicCode import config
from SPublicCode.Public_code import Connect_to_DB
from SPublicCode.Judge_Status import Judge
from SPublicCode.Bulid_Log import Log

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_search_id = sys.argv[3]
# pagenumber = sys.argv[4]
# perpage = sys.argv[5]

url = 'http://www.gsxt.gov.cn/%7B2B8UGsQnqIpxjXy1gmBFk67LI1IFYOEbBUapwrzrnWe3dHvQJfF-a4ZPewr_et4-jnPZDG01pE6vc2J-ExPdLH2qHn4JrMfsOW0Wrq6nFoA-1502264834600%7D'
gs_basic_id = 229422000
gs_search_id = 837
pagenumber = 1
perpage = 0
share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code,ra_date, ra_ways, true_amount,reg_amount,ta_ways,ta_date,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'



class Shareholder:
    def name(self,data):
        information = {}
        datalist = data
        # print data
        for i in range(len(datalist)):
            data = datalist[i]
            name = data["inv"]
            license_code = data["bLicNo"]
            license_code = deal_lable(license_code)
            types = data["invType_CN"]
            types = deal_lable(types)
            license_type = data["blicType_CN"]
            detail_check = data["detailCheck"]

            if detail_check == "true":
                detail_key = data["invId"]
                detail_url = "http://www.gsxt.gov.cn/corp-query-entprise-info-shareholderDetail-%s.html" % detail_key
                #print detail_url
                ra_date, ra_ways, true_amount,reg_amount, ta_ways, ta_date= self.deal_detail_content(detail_url)
            else:
                logging.info('无 shareholder 详情信息')
                ra_date, ra_ways, true_amount, reg_amount, ta_ways, ta_date = None, None, None, None, None, None
            information[i] = [name, license_code, license_type, types, ra_date, ra_ways, true_amount, reg_amount, ta_ways,
                              ta_date]
        return information


    def deal_detail_content(self,detail_url):
        # print detail_url
        detail_code, status_code = Send_Request().send_requests(detail_url)
        if status_code == 200:
            detail_code = json.loads(detail_code)["data"]
            if len(detail_code[1]) ==0:
                ra_date, ra_ways, true_amount = None,None,None
                reg_amount, ta_ways, ta_date = None,None,None
            else:
                if len(detail_code[1]) != 0:
                    content1 = detail_code[1][0]
                elif len(detail_code[0]) != 0:
                    content1 = detail_code[0][0]
                if len(content1) != 0:
                    if "conDate" in content1.keys():
                        ra_date = content1["conDate"]
                        ra_date = change_date_style(ra_date)
                        ta_date = ra_date
                    else:
                        ta_date = None
                        ra_date = None
                    if "conForm_CN" in content1.keys():
                        ra_ways = content1["conForm_CN"]
                        ta_ways = ra_ways
                    else:
                        ta_ways = None
                        ra_ways = None
                    if "subConAm" in content1.keys():
                        reg_amount = content1["subConAm"]
                    else:
                        reg_amount = None
                    if "acConAm" in content1.keys():
                        true_amount = content1["acConAm"]
                    else:
                        true_amount = None
                else:
                    ra_date, ra_ways, true_amount = None, None, None
                    reg_amount, ta_ways, ta_date = None, None, None
        else:
            ra_date, ra_ways, true_amount = None, None, None
            reg_amount, ta_ways, ta_date = None, None, None
        return ra_date, ra_ways, true_amount, reg_amount, ta_ways, ta_date


    def update_to_db(self,gs_basic_id, cursor, connect, information):
        cate = 0
        insert_flag,update_flag = 0,0
        remark = 0
        try:
            for key in information.keys():
                name, license_code, license_type = information[key][0], information[key][1], information[key][2]
                types, ra_date, ra_ways, true_amount = information[key][3], information[key][4], information[key][5], \
                                                       information[key][6]
                reg_amount, ta_ways, ta_date = information[key][7], information[key][8], information[key][9]
                count = cursor.execute(select_string, (gs_basic_id, name, types, cate))

                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(share_string, (
                            gs_basic_id, name, cate, types, license_type, license_code, ra_date, ra_ways, true_amount,
                            reg_amount, ta_ways, ta_date, updated_time))
                    insert_flag += rows_count
                    connect.commit()

        except Exception, e:
            remark = 100000006
            logging.error("shareholder error:%s" % e)
        finally:
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag
def main():
    Log().found_search_log(gs_search_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    Judge(connect, cursor, gs_basic_id, url,pagenumber, perpage).update_branch(Shareholder, "share")
    cursor.close()
    connect.close()

if __name__ =="__main__":
    main()
