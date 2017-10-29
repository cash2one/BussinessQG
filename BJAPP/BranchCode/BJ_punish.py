#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_punish.py
# @Author: Lmm
# @Date  : 2017-09-07
# @Desc  : 获取行政处罚信息，并将信息插入到数据库中

from PublicCode import config
from lxml import etree
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import logging
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import time
import hashlib

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=040116&ent_id=197A3E86527C570DE050007F01007DB1&chr_id=4A466BA0CD1801B2E053D400000501B2&info_categ_name=警示信息 >> 行政处罚 '
gs_basic_id = '1'
gs_py_id = '1'
punish_string = 'insert into gs_punish(gs_basic_id, id, number, types,  date,  gov_dept, name, basis,pdfurl,result,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'
update_punish_py = 'update gs_py set gs_py_id = %s, gs_punish = %s ,updated = %s where gs_py_id = %s'


class Punish:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding="utf-8"))
			dl = result.xpath("//div[@class = 'viewBox']//dl")[0]
			dlcontent = etree.tostring(dl)
			string = '<dd style="border-top:1px dashed #ccc;">'
			dllist = dlcontent.split(string)
			dllist.remove(dllist[-1])
			for i, single in enumerate(dllist):
				single = etree.HTML(single, parser=etree.HTMLParser(encoding="utf-8"))
				string = u"主体名称"
				name = self.deal_dd_content(string, single)
				string = u"行政处罚决定书文号"
				number = self.deal_dd_content(string, single)
				string = u"处罚事由"
				types = self.deal_dd_content(string, single)
				string = u"处罚依据"
				basis = self.deal_dd_content(string, single)
				string = u"处罚结果"
				result = self.deal_dd_content(string, single)
				# print result
				string = u"处罚决定日期"
				date = self.deal_dd_content(string, single)
				string = u"处罚机构"
				gov_dept = self.deal_dd_content(string, single)
				info[i] = [name, number, types, basis, result, date, gov_dept]
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
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		logging.info("punish total:%s" % total)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				name, number, types = information[key][0], information[key][1], information[key][2]
				basis, result, date = information[key][3], information[key][4], information[key][5]
				gov_dept = information[key][6]
				count = cursor.execute(select_punish, (gs_basic_id, number))
				pdfurl = ''
				if count == 0:
					m = hashlib.md5()
					m.update(str(number))
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(punish_string, (
						gs_basic_id, id, number, types, date, gov_dept, name, basis, pdfurl, result, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			print e
			remark = 100000006
			logging.error("punish error:%s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
				logging.info("execute punish:%s" % remark)
			# print remark
			return remark, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'punish'
	flag = Judge_status().judge(gs_basic_id, name, Punish, url)
	Judge_status().update_py(gs_py_id, update_punish_py, flag)


if __name__ == '__main__':
	main(gs_py_id, gs_basic_id, url)
