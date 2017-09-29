#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_web.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得江苏网站信息
from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Judge
import json
import time
import logging
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

web_string = 'insert into gs_report_web(gs_basic_id,province,gs_report_id,name,types,website,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'

web_py = 'update gs_py set gs_py_id = %s,report_web = %s,updated = %s where gs_py_id = %s'
class Report_Web:
	def __init__(self, url, headers):
		self.url = url
		self.headers = headers
	def get_info(self):
		info = {}
		result,status_code = Send_Request(self.url,self.headers).send_request()
		if status_code == 200:
			flag = 1
			data = json.loads(result.content)
			for i,singledata in enumerate(data):
				types = singledata["WEB_TYPE"]
				name = singledata["WEB_NAME"]
				website = singledata["WEB_URL"]
				info[i] = [types, name, website]
		else:
			flag = 100000004
		return info, flag
	
	
	def update_to_db(self, gs_report_id, gs_basic_id, cursor, connect, info):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key in info.keys():
				name, types, website = info[key][1], info[key][0], info[key][2]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(gs_report_id) + str(key))
				uuid = m.hexdigest()
				if name == '0' or website == '0' or name == '无' or website == '无':
					logging.info('网站信息为零')
				else:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(web_string,
										(gs_basic_id, config.province, gs_report_id, name, types, website, uuid, updated_time,
										  updated_time))
					connect.commit()
					insert_flag += flag
		except Exception, e:
			remark = 100000006
			logging.error('web error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
def main(report_id,gs_report_id,cursor,connect,gs_basic_id,gs_py_id):
	pattern = "report_web"
	url = config.main_branch_url
	headers = config.headers
	types = config.key_params["report_web"]
	url = url + config.report_params1.format(types,report_id)
	object = Report_Web(url,headers)
	info,flag = object.get_info()

	flag = Judge().update_report_info(flag, info, gs_report_id, gs_basic_id, cursor, connect, pattern)
	Judge().update_py(gs_py_id, web_py, flag)