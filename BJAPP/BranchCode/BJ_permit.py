#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_permit.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取行政许可信息，并将数据库插入到数据库中
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
from lxml import etree
import logging
import time

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!qy.dhtml?id=FDDEF056FF924AADA61CD5F844642F6C&scztdj=&credit_ticket=FD1A70E2C32F0F2D62FA303FEB321AA6'
gs_basic_id = 1
gs_py_id = 1
select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s '
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,status,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_permit_py = 'update gs_py set gs_py_id = %s ,gs_permit = %s ,updated = %s where gs_py_id = %s'


class Permit:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			ddlist = result.xpath("//div[@class='viewBox']//dl")[0]
			string = u"主体名称"
			name = self.deal_dd_content(string, ddlist)
			if u"许可证名称" in content:
				string = u"许可证名称"
				filename = self.deal_dd_content(string, ddlist)
			elif u"项目名称" in content:
				string = u"项目名称"
				filename = self.deal_dd_content(string, ddlist)
			elif u"媒介名称" in content:
				string = u"媒介名称"
				filename = self.deal_dd_content(string, ddlist)
			elif u"媒体类型" in content:
				string = u"媒体类型"
				filename = self.deal_dd_content(string, ddlist)
			elif u"证书名称" in content:
				string = u"证书名称"
				filename = self.deal_dd_content(string, ddlist)
			if u"行政许可决定书文号" in content:
				string = u"行政许可决定书文号"
				code = self.deal_dd_content(string, ddlist)
			elif u"许可证号" in content:
				string = u"许可证号"
				code = self.deal_dd_content(string, ddlist)
			elif u"准予通知书号" in content:
				code = self.deal_dd_content(string, ddlist)
			if u"许可内容" in content:
				string = u"许可内容"
				contents = self.deal_dd_content(string, ddlist)
			elif u"许可事项" in content:
				string = u"许可事项"
				contents = self.deal_dd_content(string, ddlist)
			elif u"发布范围" in content:
				string = u"发布范围"
				contents = self.deal_dd_content(string, ddlist)
			else:
				contents = None
			if u"许可决定日期" in content:
				string = u"许可决定日期"
				start_date = self.deal_dd_content(string, ddlist)
				if start_date == u"长期":
					start_date = "9999-12-31"
				elif start_date == u'':
					start_date = '0000-00-00'
			elif u"起始日期" in content:
				string = u"起始日期"
				start_date = self.deal_dd_content(string, ddlist)
				if start_date == u'':
					start_date = '0000-00-00'
			elif u"有效期自" in content:
				string = u"有效期自"
				start_date = self.deal_dd_content(string, ddlist)
				if start_date == u"":
					start_date = '0000-00-00'
			else:
				start_date = '0000-00-00'
			if u"到期日期" in content:
				string = u"到期日期"
				end_date = self.deal_dd_content(string, ddlist)
				if end_date == u'':
					end_date = '0000-00-00'
			elif u"有效期至" in content:
				string = u"有效期至"
				end_date = self.deal_dd_content(string, ddlist)
				if end_date == u"":
					end_date = '0000-00-00'
			else:
				end_date = '0000-00-00'
			if u"当前状态" in content:
				string = u"当前状态"
				status = self.deal_dd_content(string, ddlist)
			elif u"是否注销" in content:
				string = u"是否注销"
				status = self.deal_dd_content(string, ddlist)
			else:
				status = None
			string = u"机关"
			gov_dept = self.deal_dd_content(string, ddlist)
			info[0] = [name, filename, code, contents, start_date, status, gov_dept, end_date]
		else:
			flag = 100000004
		return info, flag
	
	def deal_dd_content(self, string, ddlist):
		dd = ddlist.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, information, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		logging.info("permit total:%s" % total)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				name, filename, code, content = information[key][0], information[key][1], information[key][2], \
												information[key][3]
				start_date, status, gov_dept = information[key][4], information[key][5], information[key][6]
				end_date = information[key][7]
				count = cursor.execute(select_string, (gs_basic_id, filename, code, start_date, end_date))
				id = ''
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(permit_string, (
						gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, status,
						updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			print e
			remark = 100000006
			logging.error("permit error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
				logging.info("execute permit:%s" % remark)
			return remark, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, urllist):
	Log().found_log(gs_py_id, gs_basic_id)
	object = Permit()
	name = 'permit'
	mark, number, insert_total, update_total = 0, 0, 0, 0
	for i, single in enumerate(urllist):
		time.sleep(0.5)
		# print single
		if "变更" in single:
			pass
		else:
			info, remark = object.name(single)
			if remark == 1:
				flag, total, insert, update = object.update_to_db(info, gs_basic_id)
				if flag < 100000001:
					number += 1
					insert_total += insert
					update_total += update
	if insert_total + update_total == 0:
		mark = 100000006
	else:
		mark = insert_total + update_total
	string = '%s:' % name + str(mark) + '||' + str(number) + '||' + str(insert_total) + '||' + str(update_total)
	print string
	Judge_status().update_py(gs_py_id, update_permit_py, mark)


if __name__ == '__main__':
	main(gs_py_id, gs_basic_id, url)
