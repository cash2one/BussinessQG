#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得江苏企业年报信息

from PublicCode import config
from PublicCode.Public_Code import Send_Request
from PublicCode.Public_Code import Connect_to_DB
from PublicCode import deal_html_code
import JSU_report_basic
import JSU_report_assure
import JSU_report_invest
import JSU_report_lab
import JSU_report_schange
import JSU_report_share
import JSU_report_web
import JSU_report_permit
import logging
import time
import json
import hashlib

headers = config.headers

select_basic_year = 'select reg_date from gs_basic where gs_basic_id = %s'
select_report = 'select gs_report_id from gs_report where gs_basic_id = %s and year = %s '
hide_report = 'insert into gs_report(gs_basic_id,year,province,name,uuid,code,ccode,source,report_mode,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'


class Report:
	def __init__(self, url, headers, org, id, seqid, regno,gs_basic_id):
		self.url = url
		self.headers = headers
		self.org = org
		self.id = id
		self.seqid = seqid
		self.regno = regno
		self.gs_basic_id = gs_basic_id
		
	#用于获得年报的链接
	def get_report_href(self):
		result, status_code = Send_Request(self.url, self.headers).send_request()
		info = {}
		if status_code == 200:
			flag = 1
			data = json.loads(result.content)["data"]
			if data !=None:
				for i, singledata in enumerate(data):
					report_id = singledata["ID"]
					year = singledata["REPORT_YEAR"]
					NB_TYPE = singledata["NB_TYPE"]
					info[i] = [report_id, year, NB_TYPE]
			else:
				logging.info("该企业中无年报信息")
				
		else:
			flag = 100000004
		return info, flag
	#对于网页中不展示的年报仅更新状态等几个字段
	def update_hide_report(self,cursor,connect,year):
		m = hashlib.md5()
		m.update(str(year) + str(self.gs_basic_id))
		uuid = m.hexdigest()
		name = '12'
		code = '12'
		ccode = '12'
		source = 0
		report_mode = '不公示'
		try:
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			cursor.execute(hide_report, (
			self.gs_basic_id, year, config.province, name, uuid, code, ccode, source, report_mode, updated_time, updated_time))
			connect.commit()
			remark = 0
		except Exception,e:
			logging.error("update hide error:%s"%e)
			remark = 100000006
		finally:
			return remark
	#用于更新一年的年报数据
	def update_single_report_info(self,year,report_id,cursor,connect):
		remark = 0
		try:
			main_url = config.main_branch_url
			headers = config.headers
			types = config.key_params["report_basic"]
			basic_url = main_url + config.report_params1.format(types, report_id)
			basic_object = JSU_report_basic.Report_Basic(basic_url, headers)
			baseinfo, runinfo, flag = basic_object.get_info()
			if flag == 1:
				gs_report_id = basic_object.update_report_basic(cursor, connect, self.gs_basic_id, baseinfo, year)
				basic_object.update_report_run(cursor, connect, self.gs_basic_id, runinfo, gs_report_id, year)
				JSU_report_assure.main(report_id, gs_report_id, cursor, connect, self.gs_basic_id)
				JSU_report_invest.main(report_id, gs_report_id, cursor, connect, self.gs_basic_id)
				JSU_report_permit.main(report_id, gs_report_id, cursor, connect, self.gs_basic_id)
				JSU_report_schange.main(report_id, gs_report_id, cursor, connect, self.gs_basic_id)
				JSU_report_share.main(report_id, gs_report_id, cursor, connect, self.gs_basic_id,self.org, self.id, self.seqid,self.regno,)
				JSU_report_web.main(report_id, gs_report_id, cursor, connect, self.gs_basic_id)
				if int(year) ==2016:
					JSU_report_lab.main(report_id, gs_report_id, cursor, connect,self.gs_basic_id)
				else:
					pass
			else:
				logging.info("打开基本信息年报链接失败")
		except Exception, e:
			#print e
			remark = 100000006
			logging.info("report error:%s" % e)
		finally:
			if remark <100000006:
				remark = flag
			return remark
	
		
	
	
def get_all_report_info(info, object, cursor, connect,gs_basic_id):
	total = len(info)
	insert = 0
	for key in info.keys():
		report_id,year,NB_TYPE = info[key][0], info[key][1], info[key][2]
		#判断该年年报是否存在
		count = cursor.execute(select_report, (gs_basic_id, year))
		if int(count) > 0:
			pass
		elif NB_TYPE == "hide":
			object.update_hide_report(cursor, connect, year)
		elif NB_TYPE =="show":
			remark = object.update_single_report_info(year,report_id,cursor,connect)
			
			if remark <100000001:
				insert+=1
		else:
			pass
	return total,insert
			
			
def report_main(org, id, seqid, regno, gs_basic_id):
	remark = 0
	total, insert = 0, 0
	try:
		types = config.key_params["report"]
		url = config.main_branch_url + config.branch_params.format(types, org, id, seqid,regno)
		object = Report(url, headers, org, id, seqid,regno,gs_basic_id)
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		#从数据库中选择成立日期
		now_year = time.localtime(time.time())[0]
		select_string = select_basic_year % gs_basic_id
		cursor.execute(select_string)
		reg_date = cursor.fetchall()[0][0]
		if reg_date == None or reg_date == '':
			logging.info("数据库中无成立日期")
		else:
			reg_year = str(reg_date)[0:4]
		if now_year == int(reg_year):
			flag = -1
			logging.info("该企业无年报")
		else:
			info, flag = object.get_report_href()
			if flag == 1:
				if len(info) == 0:
					flag = -1
				else:
					total, insert = get_all_report_info(info, object, cursor, connect,gs_basic_id)
			else:
				logging.info("打开网页链接失败")
	except Exception, e:
		flag = 100000005
		logging.error("error:%s" % e)
	finally:
		cursor.close()
		connect.close()
		if total > 0 and flag < 100000001:
			remark = insert
		else:
			remark = flag
		
		return remark, total, insert
		
		
def main(gs_basic_id, org, id, seqid, regno):
	remark, total, insert = report_main(org, id, seqid, regno, gs_basic_id)
	print "report:"+str(remark)+"||"+str(total)+"||"+str(insert)
	

