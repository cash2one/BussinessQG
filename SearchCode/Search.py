#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Search.py
# @Author: Lmm
# @Date  : 2017-08-23
# @Desc  : 用于四省App的实时搜索
from SPublicCode import config
from SPublicCode import deal_html_code
from SPublicCode.Public_code import Connect_to_DB
import json
import requests
import sys
import time
import logging
import hashlib

keyword = sys.argv[1]
user_id = sys.argv[2]
unique_id = sys.argv[3]
province = sys.argv[4]

# keyword = 'ywier3qrwi'
# user_id = '2'
# unique_id = '19999992'
# province = 'SHH'

log_path = config.log_path
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=log_path + '/log/py_search_%s_%s_%s.log' % (
                            time.strftime("%Y-%m-%d", time.localtime()), user_id,unique_id),
                    filemode='w')
insert_string = "insert into gs_basic(id,province,name,code,ccode,legal_person,reg_date,status,updated ) values ( %s, %s,%s,%s, %s,%s,%s, %s,%s)"
update_string = "update gs_basic set gs_basic_id = %s,name = %s ,legal_person = %s ,status = %s ,reg_date = %s,uuid = %s where gs_basic_id = %s"
update_ccode = 'update gs_basic set gs_basic_id = %s,ccode = %s ,name = %s,legal_person = %s,status =%s,reg_date=%s,uuid = %s where gs_basic_id =%s'
search_string = 'insert into gs_search(gs_basic_id,user_id,token,keyword,name,province,code,ccode,legal_person,reg_date,status,if_new,uuid,created)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s '
select_string1 = 'select gs_basic_id,uuid from gs_basic where code= %s or ccode = %s'
select_string2 = 'select gs_basic_id,uuid from gs_basic where code = %s or ccode = %s'
update_basic = 'update gs_basic_exp set gs_basic_exp_id =%s,gs_basic_id = %s,history = %s,updated = %s where gs_basic_exp_id = %s'
class Search_Info:
    def get_index(self,string,province):
        first_url = config.url_list[province].format(string)
        result= requests.get(first_url)
        status_code = result.status_code
        result = result.content
        second_url_list = {}
        if status_code ==200:
            info = json.loads(result)["info"]
            if len(info)!=0:
                info = json.loads(result)["info"]
                for i,single in enumerate(info):
                    uuid = single["uuid"]
                    url = config.detail_list[province].format(uuid)
                    legal_person = single["lerep"]
                    status = single["opState"]
                    if "uniScid" in single.keys():
                        ccode = single["uniScid"]
                        if ccode == None:
                            ccode = ''
                    else:
                        ccode = ''
                    dates = single["estDate"]
                    dates = deal_html_code.change_chinese_date(dates)
                    if "regNo" in single.keys():
                        code = single["regNo"]
                        if code ==None:
                            code = ''
                    else:
                        code = ''
                    company = single["entName"]
                    second_url_list[i] = [url,company,legal_person,status,ccode,dates,code,province]
                flag = 1
            else:
                flag = 100000003
        else:
            flag = 100000001
        return second_url_list,flag
    #将搜索信息插入到数据库中
    def insert_search(self,keyword,user_id,info,cursor,connect):
        insert_flag, update_flag = 0, 0
        remark = 0
        try:
            flag = len(info)
            for key in info.keys():
                url = info[key][0]
                company = info[key][1]
                legal_person = info[key][2]
                status = info[key][3]
                ccode = info[key][4]
                dates = info[key][5]
                code = info[key][6]
                province = info[key][7]
                if code !='' and ccode !='':
                    count = cursor.execute(select_string, (code, ccode))
                elif ccode =='':
                    count = cursor.execute(select_string1,(code,code))
                elif code =='':
                    count = cursor.execute(select_string,(ccode,ccode))
                if int(count) == 0:
                    if_new = 1
                    gs_basic_id = 0
                    uuid = 'S'
                    gs_basic_id = self.update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)
                    updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

                    row_count = cursor.execute(search_string, (
                    gs_basic_id, user_id, unique_id, keyword, company, province, code, code, legal_person, dates, status, if_new, url, updated))
                    connect.commit()
                    insert_flag += row_count
                elif int(count) == 1:
                    if_new = 0
                    uuid = 'S'
                    updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    gs_basic_id = cursor.fetchall()[0][0]
                    self.update_to_basic(int(count), info[key], cursor, connect, gs_basic_id, uuid)

                    row_count = cursor.execute(search_string, (
                        gs_basic_id, user_id, unique_id, keyword, company, province,code, ccode, legal_person, dates, status, if_new, url, updated))
                    connect.commit()
                    insert_flag += row_count
                    update_flag += 1
                elif int(count) >= 2:
                    if_new = 0
                    updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    list = {}
                    basic_id = None
                    for gs_basic_id, uuid in cursor.fetchall():
                        list[gs_basic_id] = uuid
                        if basic_id == None:
                            if uuid == 'S':
                                basic_id = gs_basic_id
                    if basic_id == None:
                        basic_id = gs_basic_id
                    for gs_basic_id in list.keys():
                        remark = 1
                        if gs_basic_id == basic_id:
                            uuid = 'S'
                        else:
                            uuid = 'R'
                        self.update_to_basic(remark, info[key], cursor, connect, gs_basic_id, uuid)

                    counts = cursor.execute(search_string, (
                        basic_id, user_id, unique_id, keyword, company, province, code, ccode, legal_person, dates, status, if_new, url, updated))
                    connect.commit()
                    insert_flag += counts
                    update_flag += count
        except Exception, e:
            remark = 100000006
            logging.error("update error:%s" % e)
        finally:
            if remark < 100000001:
                remark = flag
            return remark, insert_flag, update_flag


    #将搜索信息更新到basic表中
    def update_to_basic(self,count,info,cursor,connect,gs_basic_id,uuid):
        company = info[1]
        legal_person = info[2]
        status = info[3]
        ccode = info[4]
        dates = info[5]
        code = info[6]
        province = info[7]
        if count == 0:
            m = hashlib.md5()
            m.update(code)
            id = m.hexdigest()
            updated = deal_html_code.get_befor_date()
            #updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cursor.execute(insert_string,((id, province, company, code, ccode,legal_person,dates, status, updated)))
            gs_basic_id = connect.insert_id()
            connect.commit()
            return gs_basic_id
        elif count == 1:
            if ccode== '':
                #updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                cursor.execute(update_ccode,(gs_basic_id,code,company,legal_person,status,dates,uuid,gs_basic_id))
                connect.commit()
            elif ccode !='':
                #updated = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                cursor.execute(update_string,(gs_basic_id,company,legal_person,status,dates,uuid,gs_basic_id))
                connect.commit()
            return 0
    def printinfo(self,flag,insert_flag,update_flag):
        print_info={
            "flag":0,
            "insert":0,
            "update":0,
            "unique":0
        }
        print_info["flag"] = int(flag)
        print_info["insert"] = int(insert_flag)
        print_info["update"] = int(update_flag)
        print_info["unique"] = unique_id
        print print_info

# 函数入口
def main():
    update_flag = 0
    insert_flag = 0
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        searchobject = Search_Info()
        second_url_list, flag = searchobject.get_index(keyword,province)
        if flag ==1:
            flag, insert_flag, update_flag = searchobject.insert_search(keyword,user_id,second_url_list,cursor,connect)
        searchobject.printinfo(flag,insert_flag,update_flag)
    except Exception,e:
        print e
        logging.error("error:%s"%e)
    finally:
        cursor.close()
        connect.close()

main()