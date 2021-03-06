#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Public_code.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 创建了几个公共类用于连接数据库，发送请求


import json
import logging
import random
import time
import config
import MySQLdb
import requests
import re

# 用于连接数据库
class Connect_to_DB:
    def ConnectDB(self, HOST, USER, PASSWD, DB, PORT):
        "Connect MySQLdb and Print version."
        connect, cursor = None, None
        i = 10
        while i>0:
            try:
                connect = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8')
                cursor = connect.cursor()
                logging.info("connect is success!")
                break
            except Exception, e:
                i = i-1
                logging.error(e)
        return connect, cursor


# 用于发送请求
class Send_Request:
    def send_requests(self, url, num=1):
        list = []
        soup,status_code = None,None
        for i in range(0, 20):
            temp = random.randint(0, 9)
            list.append(temp)
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/%s%s%s.%s%s (KHTML, like Gecko) Chrome/%s%s.%s.%s%s%s%s.%s%s%s Safari/%s%s%s.%s%s\
                    ' % (
            list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10],
            list[11],
            list[12], list[13], list[14], list[15], list[16], list[17], list[18], list[19])
        headersfirst = {
            "Host": "www.gsxt.gov.cn",
            "Proxy-Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8"
        }
     
        try:
            if num > 0:
                logging.info('there remains %s times to send requests ' % (num - 1))
                html = requests.get(url, headers=headersfirst, timeout=5)
                status_code = html.status_code
                logging.info('the status_code is %s ' % status_code)
                if status_code == 200:
                    soup = html.content
        except Exception, e:
            logging.error(e)
            time.sleep(random.randint(0, 1))
            return self.send_requests(url, num=num - 1)

        if soup == None:
            print "网站暂时无法访问！！!"
            logging.error('网站暂时无法访问！！!')
            return soup, status_code
        else:
            return soup, status_code


# 用于获得各个分页的内容
class Get_BranchInfo:
    def judge_branch(self,report_id,gs_basic_id,url_pattern,QGGS_branch,name,data):
        information = QGGS_branch().name(data)
        if report_id == None and name != 'mort':
            flag, insert_flag, update_flag = QGGS_branch().update_to_db(gs_basic_id,  information)
        elif name == 'mort':
            flag, insert_flag, update_flag = QGGS_branch().update_to_db(self.gs_py_id, gs_basic_id,
                                                                        information)
        else:
           
            flag, insert_flag, update_flag = QGGS_branch().update_to_db(report_id, gs_basic_id,
                                                                        information)
            
        return flag, insert_flag, update_flag
    def get_info(self, report_id, gs_basic_id,url_pattern, QGGS_branch, name):
        total,recordsTotal = 0,-1
        insert_total,update_total = 0,0
        result, status_code = Send_Request().send_requests(url_pattern)
        if status_code == 404:
            total = 100000004
        elif status_code == 200:
            pattern = re.compile(r'<html>.*</html>|.*index/invalidLink.*')
            fail = re.findall(pattern, result)
        if status_code!=200:
            total = 100000004
            logging.info('网页打开出错！！')
        elif status_code == 200 and len(fail)==0:
            data = json.loads(result)["data"]
            recordsTotal = json.loads(result)["recordsTotal"]
            if recordsTotal == 0 and len(data)!= 0 :
                recordsTotal = len(data)
            elif recordsTotal!=0 and len(data)==0:
                recordsTotal = 0
            elif recordsTotal ==None:
                recordsTotal =0
            print "%s: %s" % (name, recordsTotal)
            logging.info("%s: %s" % (name, recordsTotal))
            totalPage = json.loads(result)["totalPage"]
            if recordsTotal ==0 and len(data) ==0:
                totalPage =0
            perpage = json.loads(result)["perPage"]
            if totalPage == 0 and recordsTotal!= 0:
                page = 1
            else:
                page = totalPage
            if page == 0:
                logging.info('暂无 %s信息' % name)
            elif page == 1:
                flag,insert_flag,update_flag = self.judge_branch(report_id,gs_basic_id,url_pattern,QGGS_branch,name,data)
                
            elif page > 1:
                flag,insert_flag,update_flag = self.judge_branch(report_id, gs_basic_id, url_pattern, QGGS_branch, name, data)
                total += flag
                insert_total += insert_flag
                update_total += update_flag
                for i in range(1, page):
                    start = perpage * i
                    url = url_pattern + '?start=%s' % start
                    result, status_code = Send_Request().send_requests(url)
                    data = json.loads(result)["data"]
                    flag,insert_flag,update_flag = self.judge_branch(report_id, gs_basic_id,url_pattern, QGGS_branch, name,
                                             data)
                    total += flag
                    insert_total += insert_flag
                    update_total += update_flag
          
        logging.info('execute %s: %s' % (name, total))
        print 'execute %s: %s' % (name, total)

        return recordsTotal,total,insert_total,update_total






