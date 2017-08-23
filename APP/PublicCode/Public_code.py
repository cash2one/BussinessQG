#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import time
import config
import MySQLdb
import random
import requests




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

class Log:
    def found_log(self,gs_py_id, gs_basic_id):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_appupdate_%s_%s_%s.log' % (
                            time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_py_id),
                            filemode='a')

class Judge_status:
    def judge(self,remark,total):
        if total ==0:
            flag = -1
        elif total >0 and remark>=0 and remark<100000001:
            flag = remark
        elif total >-1 and remark >100000001:
            flag = 100000006
        return flag

    def updaye_py(self,gs_py_id,gs_basic_id,APP,name,data,update_py):
        try:
            HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
            connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
            info = APP().name(data)
            flag,total,insert,update = APP().update_to_db(cursor, connect, gs_basic_id,info)
            flag = self.judge(flag,total)
            string = '%s:'%name+str(flag)+'||'+str(total) +'||'+str(insert)+'||'+str(update)
            print string
            if flag ==-1:
                pass
            else:
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(update_py,(gs_py_id,flag,updated_time,gs_py_id))
                connect.commit()
        except Exception,e:
            logging.error("judge error :%s"%e)
        finally:
            cursor.close()
            connect.close()








