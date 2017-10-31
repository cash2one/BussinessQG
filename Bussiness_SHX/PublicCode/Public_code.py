#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Public_code.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 创建了几个公共类用于连接数据库，发送请求




import random

import config
import MySQLdb
import requests

import logging
import time


# 用于连接数据库
class Connect_to_DB:
	def ConnectDB(self, HOST, USER, PASSWD, DB, PORT):
		"Connect MySQLdb and Print version."
		connect, cursor = None, None
		i = 10
		while i > 0:
			try:
				connect = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8')
				cursor = connect.cursor()
				logging.info("connect is success!")
				break
			except Exception, e:
				i = i - 1
				logging.error(e)
		return connect, cursor


# 用于发送请求
class Send_Request:
	def send_requests(self, url, headers, num=2):
		soup, status_code = None, None
		try:
			if num > 0:
				logging.info('there remains %s times to send requests ' % (num - 1))
				html = requests.get(url, headers=headers, timeout=15)
				status_code = html.status_code
				logging.info('the status_code is %s ' % status_code)
				if status_code == 200:
					soup = html.text
		except Exception, e:
			logging.error(e)
			time.sleep(random.randint(0, 1))
			return self.send_requests(url, headers=headers, num=num - 1)
		
		if soup == None:
			print '网站暂时无法访问'
			logging.error('网站暂时无法访问！！!')
			return soup, status_code
		else:
			return soup, status_code


class Log:
	def __init__(self):
		pass
	
	# self.gs_basic_id = gs_basic_id
	
	# 自动创建文件夹检查是否存在文件夹返回当前路径，不存在则创建文件
	def mkdir_floder(self):
		import os
		import sys
		# 这个获取的是最开始的执行路径，验证一下即可知道与下面的差别
		# current_path = os.getcwd()
		# 用于获取当前被执行文件的路径
		current_path = sys.path[0]
		# 判断路径是否存在，存在True,不存在False
		isExists = os.path.exists(current_path + '/log')
		if not isExists:
			os.mkdir('log')
		return current_path
	
	def found_log(self, gs_search_id, gs_basic_id):
		# log_path = self.mkdir_floder()
		log_path = config.log_path
		logging.basicConfig(level=logging.DEBUG,
							format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
							datefmt='%a, %d %b %Y %H:%M:%S',
							filename=log_path + '/log/py_SHX_update_%s_%s_%s.log' % (
								time.strftime("%Y-%m-%d", time.localtime()), gs_search_id, gs_basic_id),
							filemode='a')


# 用于判断程序运行的状态,这一步部分的编写最为麻烦，需要刚开始搭建代码结构时，进行分析
# 后面整合代码进一步完善，每一步分信息所需要的参数不同，据需要进行调整
class Judge:
	# 传递尽力prirpid,详情链接，企业名称，传递给需要的这几项信息的分项信息
	def __init__(self, pripid, url, name):
		self._pripid = pripid
		self._url = url
		self._name = name.decode("utf-8").encode("gb2312")
	
	# 将数据更新到数据库中
	def update_info(self, pattern, Branch, data, gs_basic_id):
		total, insert_flag, update_flag = 0, 0, 0
		if pattern == "change" or pattern == "check" or pattern == "clear" or pattern == "stock" or pattern == "person" or pattern == "punish2" or pattern == "branch":
			object = Branch()
		# 商标部分较为特殊需要单独处理
		elif pattern == "brand":
			pass
		elif pattern == "except" or pattern == "permit" or pattern == "freeze" or pattern == "mort" \
				or pattern == "permit2" or pattern == 'punish' or pattern == "shareholder":
			object = Branch(self._pripid, self._url)
		elif pattern == "report":
			pass
		
		info = object.get_info(data)
		# 如果获取的信息长度为零，则代表没有信息
		if len(info) == 0:
			flag = -1
		if len(info) > 0:
			flag, total, insert_flag, update_flag = object.update_to_db(info, gs_basic_id)
		print "%s:" % pattern + str(flag) + '||' + str(total) + "||" + str(insert_flag) + '||' + str(update_flag)
