#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QGGS_shareholder.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  :用于更新发起人及出资信息

import json
import logging
import sys
import time
import re
from  PublicCode.Public_code import Send_Request as Send_Request
from PublicCode.deal_html_code import change_date_style
from PublicCode.deal_html_code import deal_lable
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Judge_Status import Judge
from PublicCode.Bulid_Log import Log
import base64
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


url = sys.argv[1]
gs_basic_id = sys.argv[2]
gs_py_id = sys.argv[3]
pagenumber = sys.argv[4]
perpage = sys.argv[5]

# url = 'http://www.gsxt.gov.cn/%7Ba8cGdSp6ifXpkAR8qkKIOpkfNYcK9YfPrCXIeYnQa1sda20_lWPh51pwIpBRvdsNr0fRVS7S_BikiJmAbMDk-yW3TzQHYWvKCzeQ4neGvuIdZRcD4pb-OhhQtRn9h7-CXqavHOrOaPG18xlGjfgO3A-1505091743115%7D'
# gs_basic_id = 1900000099
# gs_py_id = 1501
# pagenumber = 1
# perpage = 0
share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code,ra_date, ra_ways, true_amount,reg_amount,ta_ways,ta_date,country,address,iv_basic_id,ps_basic_id,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'
update_share_py = 'update gs_py set gs_py_id = %s,gs_shareholder = %s,updated = %s where gs_py_id = %s'
select_name = 'select gs_basic_id from gs_unique where name = "%s"'
select_ps = 'select ps_basic_id,gs_basic_id from ps_basic where name = "%s"'
insert_ps = 'insert into ps_basic(gs_basic_id,name,idcard,province,city,town,birthday,encode,remark,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_ps = 'update ps_basic set ps_basic_id = %s ,gs_basic_id = %s,updated = %s where ps_basic_id = %s'
update_share = 'update gs_shareholder set quit = 1 where gs_basic_id = %s and cate = 0'
update_quit = 'update gs_shareholder set quit = 0,updated = %s where gs_shareholder_id = %s and gs_basic_id = %s'

class Shareholder:
    def name(self,data):
        information = {}
        datalist = data
        # print data
        for i in range(len(datalist)):
            data = datalist[i]
            name = data["inv"]
            if data["blicType_CN"]!='':
                license_type = data["blicType_CN"]
                license_type = deal_lable(license_type)
                license_code = data["bLicNo"]
                license_code = deal_lable(license_code)
            elif data["cerType_CN"]!='':
                license_type = data["cerType_CN"]
                license_type = deal_lable(license_type)
                license_code = data["cerNo"]
                license_code = deal_lable(license_code)
            else:
                license_type = ''
                license_code = ''
            types = data["invType_CN"]
            types = deal_lable(types)

            detail_check = data["detailCheck"]
            country = data["country_CN"]
            address = data["dom"]
            if detail_check == "true":
                detail_key = data["invId"]
                detail_url = "http://www.gsxt.gov.cn/corp-query-entprise-info-shareholderDetail-%s.html" % detail_key
                
                ra_date, ra_ways, true_amount,reg_amount, ta_ways, ta_date= self.deal_detail_content(detail_url)
            else:
                logging.info('无 shareholder 详情信息')
                ra_date, ra_ways, true_amount, reg_amount, ta_ways, ta_date = '', '', '', '', '', ''
            information[i] = [name, license_code, license_type, types, ra_date, ra_ways, true_amount, reg_amount, ta_ways,
                              ta_date,country,address]
        return information


    def deal_detail_content(self,detail_url):
        # print detail_url
        detail_code, status_code = Send_Request().send_requests(detail_url)
        if status_code == 200:
            detail_code = json.loads(detail_code)["data"]
            if len(detail_code[1]) ==0:
                ra_date, ra_ways, true_amount = '','',''
                reg_amount, ta_ways, ta_date = '','',''
            else:
                if len(detail_code[1]) != 0:
                    content1 = detail_code[1][0]
                elif len(detail_code[0]) != 0:
                    content1 = detail_code[0][0]
                if len(content1) != 0:
                    if "conDate" in content1.keys():
                        ra_date = content1["conDate"]
                        ra_date = change_date_style(ra_date)
                        ta_date = '0000-00-00'
                    else:
                        
                        ra_date = '0000-00-00'
                    if "conForm_CN" in content1.keys():
                        ra_ways = content1["conForm_CN"]
                        ta_ways = ra_ways
                    else:
                        ta_ways = ''
                        ra_ways = ''
                    if "subConAm" in content1.keys():
                        reg_amount = content1["subConAm"]
                    else:
                        reg_amount = ''
                    if "acConAm" in content1.keys():
                        true_amount = content1["acConAm"]
                    else:
                        true_amount = ''
                else:
                    ra_date, ra_ways, true_amount = '0000-00-00', '', ''
                    reg_amount, ta_ways, ta_date = '', '', '0000-00-00'
        else:
            ra_date, ra_ways, true_amount = '', '', ''
            reg_amount, ta_ways, ta_date = '', '', ''
        return ra_date, ra_ways, true_amount, reg_amount, ta_ways, ta_date
    def judge_certcode(self,name,code,cursor,connect,basic_id):
        ps = 0
        if len(code) == 15 or len(code) == 18:
            select_string = select_ps % name
            count = cursor.execute(select_string)
            if int(count) == 1:
                for ps_basic_id, gs_basic_id in cursor.fetchall():
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
                if len(code) == 15:
                    birthday = code[6:12]
                elif len(code) == 18:
                    birthday = code[6:14]
                if len(code) == 15:
                    encode = base64.b64encode(code[12:15])
                elif len(code) == 18:
                    encode = base64.b64encode(code[14:18])
                gs_basic_id = '"'+str(basic_id)+'",'
                remark = ''
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(insert_ps, (gs_basic_id, name, idcard, province, city, town, birthday, encode, remark, updated_time,updated_time))
                ps = connect.insert_id()
                connect.commit()
            return ps

    def update_to_db(self,gs_basic_id, cursor, connect, information):
        cate = 0
        insert_flag,update_flag = 0,0
        remark = 0
        try:
            string = update_share % gs_basic_id
            cursor.execute(string)
            connect.commit()
            cursor.close()
            connect.close()
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            for key in information.keys():
                name, license_code, license_type = information[key][0], information[key][1], information[key][2]
                types, ra_date, ra_ways, true_amount = information[key][3], information[key][4], information[key][5], \
                                                       information[key][6]
                reg_amount, ta_ways, ta_date = information[key][7], information[key][8], information[key][9]

                country,address = information[key][10],information[key][11]
                iv_basic_id = 0
                if name!= '' or name !='':
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
                ps_basic_id = 0
                if license_type == '中华人民共和国居民身份证':
                    if license_code == '' or license_code == '':
                        license_code = '非公示项'
                    elif len(license_code) == 15 or len(license_code) == 18:
                        ps_basic_id = self.judge_certcode(name, license_code, cursor, connect, gs_basic_id)
                elif license_code == '' or license_code == '' and license_type!='':
                    license_code = '非公示项'
                else:
                    ps_basic_id = 0
                count = cursor.execute(select_string, (gs_basic_id, name, types, cate))

                if count == 0:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    rows_count = cursor.execute(share_string, (
                            gs_basic_id, name, cate, types, license_type, license_code, ra_date, ra_ways, true_amount,
                            reg_amount, ta_ways, ta_date, country,address,iv_basic_id,ps_basic_id,updated_time))
                    insert_flag += rows_count
                    connect.commit()
                elif int(count) == 1:
                    updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    gs_shareholder_id = cursor.fetchall()[0][0]
                    cursor.execute(update_quit, (updated_time, gs_shareholder_id, gs_basic_id))
                    connect.commit()
        except Exception, e:
            remark = 100000006
            logging.error("shareholder error:%s" % e)
        finally:
            cursor.close()
            connect.close()
            if remark < 100000001:
                remark = insert_flag
            return remark,insert_flag,update_flag
def main():
    Log().found_log(gs_py_id,gs_basic_id)
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    Judge(gs_py_id, connect, cursor, gs_basic_id, url,pagenumber, perpage).update_branch(update_share_py,Shareholder, "share")
    # cursor.close()
    # connect.close()

if __name__ =="__main__":
    main()
