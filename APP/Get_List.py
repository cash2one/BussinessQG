#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_List.py
# @Author: Lmm
# @Date  : 2017-08-15
# @Desc  : 用于获取列表信息

import json
import logging

from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Log
import requests
import App_Update

# code = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id = sys.argv[3]
# code = '9131000013221158XC'
# gs_basic_id = 229418511
# gs_py_id = 1
s = requests.session()
s.keep_alive = False


select_name = 'select name from gs_basic where gs_basic_id = %s'
select_basic = 'select gs_basic_id,code from gs_basic where province = "HEB" and gs_basic_id >229417812'
insert_py = 'insert into gs_py(gs_basic_id,user_id) values(%s,%s)'
#用于获取信息列表
def get_index(code):
    province = deal_html_code.judge_province(code)
    first_url = config.url_list[province].format(code)
    #print first_url
    result= requests.get(first_url)
    status_code = result.status_code
    result = result.content
    second_url = None
    entName = None
    if status_code ==200:
        info = json.loads(result)["info"]
        if len(info)!=0:
            info = json.loads(result)["info"][0]
            uuid = info["uuid"]
            entName = info["entName"]
            second_url = config.detail_list[province].format(uuid)
            flag = 1
        else:
            flag = 100000002
    else:
        flag = 100000001
    return second_url,flag,entName
def main():
    gs_user_id = 1501
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        printinfo = {
            "url": 0,
            'flag': 0
        }
        cursor.execute(select_basic)
        for gs_basic_id,code in cursor.fetchall():
            print gs_basic_id
            cursor.execute(insert_py,(gs_basic_id,gs_user_id))
            gs_py_id = connect.insert_id()
            Log().found_log(gs_py_id, gs_basic_id)
            connect.commit()

            second_url, flag, entName = get_index(code)

            if flag == 100000002:
                select_string = select_name % gs_basic_id
                cursor.execute(select_string)
                name = cursor.fetchall()[0][0]
                second_url, flag, entName = get_index(name)
                if name != entName:
                    second_url = 0
                    flag = 0
            gs_user_id+=1
            App_Update.update_all_info(gs_py_id,gs_basic_id,second_url)
            printinfo["url"] = second_url
            printinfo["flag"] = flag
            print printinfo
    except Exception, e:
        logging.info("get list error:%s" % e)
    finally:
        cursor.close()
        connect.close()
    #     printinfo["url"] = second_url
    #     printinfo["flag"] = flag
    #     print printinfo


# def main():
#     Log().found_log(gs_py_id,gs_basic_id)
#     try:
#         HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
#         connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
#         printinfo = {
#             "url":0,
#             'flag':0
#         }
#         second_url,flag,entName = get_index(code)
#         if flag == 100000002:
#             select_string = select_name % gs_basic_id
#             cursor.execute(select_string)
#             name = cursor.fetchall()[0][0]
#             second_url, flag, entName = get_index(name)
#             if name != entName:
#                 second_url = 0
#                 flag = 0
#     except Exception,e:
#         logging.info("get list error:%s"%e)
#     finally:
#         cursor.close()
#         connect.close()
#         printinfo["url"] = second_url
#         printinfo["flag"] = flag
#         print printinfo
if __name__ == "__main__":
    main()


