#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_except.py
# @Author: Lmm
# @Date  : 2017-09-07
# @Desc  : 用于获取异常名录信息，并将信息插入到数据库中

import sys
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Log
import requests
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Judge_status
import logging
import time

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=040301&ent_id=87F3E0BDCB4042EB9AC42F692AABC2EE&chr_id=3b9a3ece8fe24074836eb607111d866e&info_categ_name=%E8%AD%A6%E7%A4%BA%E4%BF%A1%E6%81%AF%20%3E%3E%20%E7%BB%8F%E8%90%A5%E5%BC%82%E5%B8%B8%E5%90%8D%E5%BD%95'
gs_basic_id = '1900000799'
gs_py_id = '1'

except_string = 'insert into gs_except(gs_basic_id,types, in_reason, in_date,out_reason, out_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_except = 'select gs_except_id from gs_except where gs_basic_id = %s and in_date = %s'
update_except = 'update gs_except set gs_except_id = %s,types = %s ,in_reason = %s,out_reason = %s ,out_date=%s,gov_dept = %s ,updated = %s where gs_except_id = %s'
update_except_py = 'update gs_py set gs_py_id = %s,gs_except = %s,updated =%s where gs_py_id = %s'


class Except:
	def name(self, url):
		content, status_code = Send_Request().send_request(url)
		info = {}
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding="utf-8"))
			dl = result.xpath("//div[@class = 'viewBox']//dl")[0]
			dlcontent = etree.tostring(dl)
			string = '<dd style="border-top:1px dashed #ccc;">'
			dllist = dlcontent.split(string)
			dllist.remove(dllist[-1])
			for i, single in enumerate(dllist):
				types = '经营异常'
				single = etree.HTML(single, parser=etree.HTMLParser(encoding="utf-8"))
				string = u'列入原因'
				in_reason = self.deal_dd_content(string, single)
				string = u'列入日期'
				in_date = self.deal_dd_content(string, single)
				if in_date == u'':
					in_date = '0000-00-00'
				string = u'作出决定机关(列入)'
				gov_dept = self.deal_dd_content(string, single)
				string = u'移出原因'
				out_reason = self.deal_dd_content(string, single)
				string = u'移出日期'
				out_date = self.deal_dd_content(string, single)
				if out_date == u"":
					out_date = '0000-00-00'
				info[i] = [types, in_reason, in_date, gov_dept, out_reason, out_date]
		else:
			flag = 100000004
		return info, flag
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, information, gs_basic_id):
		update_flag, insert_flag = 0, 0
		remark = 0
		total = len(information)
		logging.info('except total:%s' % total)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				types, in_reason, in_date = information[key][0], information[key][1], information[key][2]
				gov_dept, out_reason, out_date = information[key][3], information[key][4], information[key][5]
				count = cursor.execute(select_except, (gs_basic_id, in_date))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(except_string, (
						gs_basic_id, types, in_reason, in_date, out_reason, out_date, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					gs_except_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(update_except, (
						gs_except_id, types, in_reason, out_reason, out_date, gov_dept, updated_time, gs_except_id))
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			print e
			remark = 100000006
			logging.error("except error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag + update_flag
				logging.info("excute except :%s" % remark)
			return remark, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'except'
	flag = Judge_status().judge(gs_basic_id, name, Except, url)
	
	# if __name__ == '__main__':
	#     main(gs_py_id,gs_basic_id,url)
