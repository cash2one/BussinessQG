#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Public_code.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 创建了几个公共类用于连接数据库，发送请求等



import logging
import random
import config
import MySQLdb
import requests
import re
import chardet
import time
import linecache

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
#用于向网页发送请求,并判断请求状态
class Send_Request:
    #向搜素列表发送请求
    def send_request(self,url):
        content = None
        try:
            
            # UA = random.choice(config.USER_AGENTS)
            # headers = config.headers_detail
            # headers["User-Agent"] = UA
            # print UA
            
            a = random.randrange(1, 1001)  # 1-9中生成随机数
            # 从文件user-agent中对读取第a行的数据
            theline = linecache.getline(r'user-agent.txt', a)
            theline = theline.replace("\n",'')
            headers = config.headers_detail
            headers["User-Agent"] = theline
            result = requests.get(url, headers=headers,timeout=5)
            status_code = result.status_code
            if status_code == 200:
                content = result.content
                pattern = re.compile(u".*无查询结果.*|.*查询结果较多.*|.*访问异常.*")
                match = re.findall(pattern, result.content)
                if chardet.detect(content)["encoding"]!="utf-8" or len(match) != 0:
                    status_code = 404
                    content = None
            else:
                content = None
        except Exception,e:
            # print e
            logging.info("request error:%s"%e)
            status_code = 404
            content = None
        finally:
            return content,status_code
    #带着cookie信息访问页面
    def send_request2(self,url,cookies):
        content = None
        try:
            UA = random.choice(config.USER_AGENTS)
            headers = config.headers_detail
            headers["User-Agent"] = UA
            # print UA
            result = requests.get(url, headers=headers, cookies=cookies, proxies=config.proxies,timeout=5)
            status_code = result.status_code
            if status_code == 200:
                content = result.content
                pattern = re.compile(u".*无查询结果.*|.*查询结果较多.*|.*访问频繁.*")
                match = re.findall(pattern, result.content)
                if chardet.detect(content)["encoding"] != "utf-8" or len(match) != 0:
                    status_code = 404
                    content = None
            else:
                content = None
        except Exception, e:
            logging.info("request error:%s" % e)
            status_code = 404
            content = None
        finally:
            return content, status_code

    def send_request3(self, url, cookies,headers):
        content = None
        try:
            result = requests.get(url, headers=headers, cookies=cookies,timeout=5)
            status_code = result.status_code
            if status_code == 200:
                content = result.content
                pattern = re.compile(u".*无查询结果.*|.*查询结果较多.*|.*访问频繁.*")
                match = re.findall(pattern, result.content)
                if chardet.detect(content)["encoding"] != "utf-8" or len(match) != 0:
                    status_code = 404
                    content = None
            else:
                content = None
        except Exception, e:
            logging.info("request error:%s" % e)
            status_code = 404
            content = None
        finally:
            return content, status_code
    

class Log:
    def found_log(self, gs_py_id, gs_basic_id):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_bjapp_update_%s_%s_%s.log' % (
                                        time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_py_id),
                            filemode='a')
#用于更新py表,及判断程序运行的状态
class Judge_status:
    def judge(self,gs_basic_id,name,BJAPP,url):
        flag, total, insert, update = 0, 0, 0, 0
        try:
            object = BJAPP()
            info, remark = object.name(url)
            if len(info) == 0 and remark == 1:
                flag = -1
            elif len(info) >0:
                flag, total, insert, update = object.update_to_db(info, gs_basic_id)
            else:
                flag = remark
        except Exception, e:
            print e
            flag = 100000005
            logging.info("unknow error:%s" % e)
        finally:
            string = '%s:' % name + str(flag) + '||' + str(total) + '||' + str(insert) + '||' + str(update)
            print string
            return flag
    def update_report_py(self,gs_py_id,update_py,flag):
        try:
            if flag ==0:
                pass
            else:
                HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
                connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(update_py, (gs_py_id, flag, updated_time, gs_py_id))
                connect.commit()
                cursor.close()
                connect.close()
        except Exception,e:
            logging.info("update py error:%s"%e)
        
        
        
    def update_py(self,gs_py_id,update_py,flag):
        try:
            if flag == -1:
                pass
            else:
                HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
                connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                cursor.execute(update_py, (gs_py_id, flag, updated_time, gs_py_id))
                connect.commit()
                cursor.close()
                connect.close()
        except Exception, e:
            logging.error("update py error :%s" % e)
          

        
    
           
            
    
        








