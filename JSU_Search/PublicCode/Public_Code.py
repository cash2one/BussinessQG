#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Public_Code.py
# @Author: Lmm
# @Date  : 2017-09-20
# @Desc  : 用于自定义一些公共函数
import logging
import re
import config
import MySQLdb
import requests
import time
import json

class Send_Request:
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
	#向网页发送一个get请求
	def send_request(self):
		result = None
		try:
			result = requests.get(self.url, headers=self.headers, timeout = 10)
			status_code = result.status_code
		except Exception, e:
			status_code = 404
			logging.error("request error:%s"%e)
		finally:
			return result, status_code
	#带着cookie的get请求
	def send_request1(self,cookies):
		result = None
		try:
			result = requests.get(self.url, headers=self.headers, cookies=cookies)
			status_code = result.status_code
		except Exception, e:
			status_code = 404
			logging.error("request error:%s" % e)
		finally:
			return result, status_code
	#向网页发送一个post请求
	def post_request(self,params):
		result = None
		try:
			result = requests.get(self.url, params, headers=self.headers)
			status_code = result.status_code
		except Exception, e:
			status_code = 404
			logging.error("request error:%s" % e)
		finally:
			return result, status_code
		
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
class Log:
    def found_log(self, gs_py_id, gs_basic_id):
        log_path = config.log_path
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=log_path + '/log/py_JSU_search_%s_%s_%s.log' % (
                                        time.strftime("%Y-%m-%d", time.localtime()), gs_basic_id, gs_py_id),
                            filemode='a')

#包含两种类型的函数防止以后页面发生变化
#用于获取页面信息
class GetBranchInfo:
    def __init__(self, url, headers,object,types):
        self.url = url
        self.headers = headers
        self.object = object
        self.types = types
    #用于获得链接样式
	#对于需要翻页的年报链接
    def get_report_url(self,report_id,currentpage):
        params = config.report_params3.format(self.types, report_id, currentpage)
        url = self.url + params
        return url
	#对于需要翻页的信息链接
    def get_branch_url(self,org, id, seqid, regno, currentpage):
        params = config.params.format(self.types, org, id, seqid, regno, currentpage)
        url = self.url + params
        return url
	
		
    #用于获得单页信息
    def get_single_page_info(self,url,info):
        result, status_code = Send_Request(url, self.headers).send_request()
        pagecount = 0
        if status_code == 200:
            flag = 1
            content = json.loads(result.content)
            data = content["data"]
            pagecount = content["pageCount"]
            self.object.deal_single_info(data, info)
        else:
            flag = 100000004
        return pagecount,flag
		
    #用于获得带分页的全部信息
    def get_info(self, org, id, seqid, regno):
		info = {}
		currentpage = 1
		url = self.get_branch_url(org, id, seqid, regno, currentpage)
		pagecount, flag = self.get_single_page_info(url, info)
		if flag == 1:
			if pagecount == 1:
				pass
			else:
				for i in xrange(2, pagecount + 1):
					currentpage = i
					url = self.get_branch_url(org, id, seqid, regno, currentpage)
					self.get_single_page_info(url, info)
		else:
			flag = 100000004
		return info, flag
		
		
	#用于获得带分页的年报的全部信息
    def get_report_info(self, report_id):
		currentpage = 1
		url = self.get_report_url(report_id,currentpage)
		info = {}
		pagecount,flag =self.get_single_page_info(url,info)
		if flag == 1:
			if pagecount == 1:
				pass
			else:
				for i in xrange(2, pagecount + 1):
					currentpage = i
					url = self.get_report_url(report_id, currentpage)
					self.get_single_page_info(url, info)
		else:
			flag = 100000004
		return info, flag
	#用于获得年报中的股东出资链接
    def get_report_share_url(self, report_id,org, id, seqid, regno, currentpage):
		params = config.report_params2.format(self.types,report_id, org, id, seqid, regno, currentpage)
		url = self.url + params
		return url
	#用于获得年报中的股东出资信息
    def get_report_share_info(self,report_id,org,id,seqid,regno):
		currentpage = 1
		url = self.get_report_share_url(report_id, org,id,seqid,regno,currentpage)
		info = {}
		pagecount, flag = self.get_single_page_info(url, info)
		if flag == 1:
			if pagecount == 1:
				pass
			else:
				for i in xrange(2, pagecount + 1):
					currentpage = i
					url = self.get_report_url(report_id, org,id,regno,currentpage)
					self.get_single_page_info(url, info)
		else:
			flag = 100000004
		return info, flag
#用于判断程序运行的状态，并将状态更新至py表
class Judge:
	#将数据更新到数据库中
	#update_info1 是针对不需要翻页的信息而言(person,branch,brand,clear)
	def update_info1(self,pattern,org,id,seq_id,regno,Branch,gs_basic_id):
		total,insert_flag,update_flag = 0,0,0
		headers = config.headers
		type = config.key_params[pattern]
		url = config.main_branch_url + config.branch_params.format(type, org, id, seq_id, regno)
		# print url
		object = Branch(url, headers)
		info, flag = object.get_info()
		if flag == 1:
			flag, total, insert_flag, update_flag = object.update_to_db(info, gs_basic_id)
			if total == 0:
				flag = -1
		print "%s:"%pattern +str(flag)+'||'+str(total)+"||" +str(insert_flag)+'||'+ str(update_flag)
		return flag
	#对于需要翻页的页面而言
	def update_info2(self,pattern,org,id,seq_id,regno,Branch,gs_basic_id):
		total, insert_flag, update_flag = 0, 0, 0
		headers = config.headers
		url = config.main_branch_url
		types = config.key_params[pattern]
		object = Branch()
		info, flag = GetBranchInfo(url, headers, object, types).get_info(org, id, seq_id, regno)
		
		if flag == 1:
			flag, total, insert_flag, update_flag = object.update_to_db(info, gs_basic_id)
			if total == 0 and flag <100000001:
				flag = -1
		logging.info("%s:"%pattern +str(flag)+'||'+str(total)+"||" +str(insert_flag)+'||'+ str(update_flag))
		print "%s:"%pattern +str(flag)+'||'+str(total)+"||" +str(insert_flag)+'||'+ str(update_flag)
		return flag
	#用于更新年报信息
	def update_report_info(self,flag,info,gs_report_id,gs_basic_id,cursor,connect,pattern):
		if flag == 1:
			flag, total, insert_flag, update_flag = object.update_to_db(gs_report_id, gs_basic_id, cursor, connect,															info)
			if total == 0 and flag < 100000001:
				flag = -1
			logging.info("execute report_%s:%s" % (pattern,flag))
		else:
			logging.info("打开report_%s链接失败！" % pattern)
		return flag
	