#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import random
import time
import MySQLdb
import requests

import config


# 用于连接数据库，如果链接失败，则重试，重试次数为十次
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

#用于向网页发送请求
class Send_Request:
    def send_requests(self, url, num=3):
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
        header = headersfirst
        try:
            if num > 0:
                logging.info('there remains %s times to send requests ' % (num - 1))
                html = requests.get(url, headers=header, timeout=5)
                status_code = html.status_code
                logging.info('the status_code is %s ' % status_code)
                if status_code == 200:
                    soup = html.content
        except Exception, e:
            logging.error(e)
            time.sleep(random.randint(0, 1))
            return self.send_requests(url, num=num - 1)

        if soup == None:
            print '网站暂时无法访问！！！'
            logging.error('网站暂时无法访问！！!')
            return soup, status_code
        else:
            return soup, status_code
#创建日志的文件
class Log:
    #自动创建文件夹
    def mkdir_floder(self):
        import os
        import sys
        # 这个获取其实是python 解释器的路径
        # current_path = os.getcwd()
        #用于获取当前被执行文件的路径
        current_path = sys.path[0]
        #判断路径是否存在，存在True,不存在False
        isExists = os.path.exists(current_path+'/log')
        if not isExists:
            os.mkdir('log')
        
        return current_path
        
    #以追加的方式创建日志文件
    def found_log(self,gs_basic_id):
        log_path = self.mkdir_floder()
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + 'update_%s_%s.log' % (
                            time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id),
                            filemode='a')
    def found_log1(self):
        log_path = self.mkdir_floder()
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/appupdate_%s.log' %
                                time.strftime("%Y-%m-%d", time.localtime()),
                            filemode='a')
        
#判断状态
class Judge_status:
    def judge(self,remark,total):
        if total ==0:
            flag = -1
        elif total >0 and remark>=0 and remark<100000001:
            flag = remark
        elif total >-1 and remark >100000001:
            flag = 100000006
        return flag

    def update_info(self, gs_basic_id, APP, name, data):
        try:
            info = APP().name(data)
            flag, total, insert, update = APP().update_to_db(gs_basic_id, info)
            flag = self.judge(flag, total)
            string = '%s:' % name+str(flag)+'||'+str(total) +'||'+str(insert)+'||'+str(update)
            print string
            logging.info(string)
        except Exception, e:
            logging.error("judge error :%s"%e)
       








