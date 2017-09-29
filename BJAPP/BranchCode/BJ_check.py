#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_check.py
# @Author: Lmm
# @Date  : 2017-09-07
# @Desc  : 用于获取抽查检查信息，并将信息插入到数据库中
import requests
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Judge_status
import time
import logging
from PublicCode.Public_code import Log
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=030103&ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&chr_id=1AFB38483F0E00E0E053A06400C300E0,&info_categ_name=%E6%8F%90%E7%A4%BA%E4%BF%A1%E6%81%AF%20%3E%3E%20%E6%8A%BD%E6%9F%A5%E4%BF%A1%E6%81%AF'
gs_basic_id = '229421869'
gs_py_id = '1'

check_string = 'insert  into gs_check(gs_basic_id,types,result,check_date,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_check = 'select gs_check_id from gs_check where gs_basic_id = %s and check_date = %s and types = %s'
update_check_py = 'update gs_py set gs_py_id = %s,gs_check = %s,updated = %s where gs_py_id = %s'
class Check:
	def name(self,url):
		info = {}
		content,status_code =Send_Request().send_request(url)
		if status_code ==200:
			flag = 1
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class='viewBox']//dl")[0]
			dlcontent = etree.tostring(dl)
			string = '<dd style="border-top:1px dashed #ccc;">'
			dllist = dlcontent.split(string)
			dllist.remove(dllist[-1])
			for i,single in enumerate(dllist):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding='utf-8'))
				# string = u"主体名称"
				# name = self.deal_dd_content(string,single)
				string = u"抽查检查日期"
				check_date = self.deal_dd_content(string,single)
				string = u"检查实施机关"
				gov_dept = self.deal_dd_content(string,single)
				string = u"抽查检查结果"
				result = self.deal_dd_content(string,single)
				if u"抽查信息" in url:
					types = "抽查"
				elif u"检查信息" in url:
					types = "检查"
				else:
					pass
				info[i] = [check_date,gov_dept,result,types]
		else:
			flag = 100000004
		# print info,flag
		return info,flag
		
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	def update_to_db(self,info,gs_basic_id):
		
		# types = '抽查'
		insert_flag = 0
		update_flag = 0
		flag = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				check_date, gov_dept, result = info[key][0],info[key][1],info[key][2]
				types = info[key][3]
				count = cursor.execute(select_check, (gs_basic_id, check_date, types))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(check_string,(gs_basic_id, types, result, check_date, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			print e
			logging.error("check error: %s" % e)
			flag = 100000006
		finally:
			if flag < 100000001:
				flag = insert_flag
				logging.info('execute check :%s' % flag)
			return flag, total, insert_flag, update_flag
def main(gs_py_id,gs_basic_id,url):
	Log().found_log(gs_py_id,gs_basic_id)
	name = 'check'
	flag = Judge_status().judge(gs_basic_id,name,Check,url)
	Judge_status().update_py(gs_py_id,update_check_py,flag)

# if __name__ == '__main__':
#     main(gs_py_id,gs_basic_id,url)
		
				