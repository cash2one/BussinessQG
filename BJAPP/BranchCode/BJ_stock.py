#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_stock.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取股权出质信息
from lxml import etree
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import logging
import requests
import time
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=030339&ent_id=CCD0D5D249B04BF4B1B40FA757E9B38E&chr_id=0E28C20A4A8C421CB163EB5F05F963E5,4A3E9E93710A48D2BB08DC3414D328E2,35FB998F83C5416D920A6538F84EEE5A,&info_categ_name=%E6%8F%90%E7%A4%BA%E4%BF%A1%E6%81%AF%20%3E%3E%20%E8%82%A1%E6%9D%83%E8%B4%A8%E6%8A%BC%E7%99%BB%E8%AE%B0%E4%BF%A1%E6%81%AF'
gs_basic_id = '1'
gs_py_id = '1'
stock_string = 'insert into gs_stock(gs_basic_id,equityno,pledgor,pled_blicno,impam,imporg,imporg_blicno,equlle_date,public_date,type,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_stock = 'select gs_stock_id from gs_stock where gs_basic_id = %s and equityNo = %s'
update_stock = 'update gs_stock set gs_basic_id = %s,pledgor = %s,pled_blicno = %s,impam = %s,imporg = %s,imporg_blicno = %s,equlle_date = %s,public_date = %s,type = %s ,updated = %s where gs_stock_id = %s'
update_stock_py = 'update gs_py set gs_py_id = %s,gs_stock = %s ,updated = %s where gs_py_id = %s'
class Stock:
	def name(self,url):
		info = {}
		content,status_code = Send_Request().send_request(url)
		# print content
		if status_code ==200:
			flag = 1
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath("//div[@class ='viewBox']//dl")[0]
			tostringinfo = etree.tostring(dl)
			list = tostringinfo.split('<dd style="border-top:1px dashed #ccc;">')
			list.remove(list[-1])
			for i,single in enumerate(list):
				single = etree.HTML(single,parser=etree.HTMLParser(encoding='utf-8'))
				string = u'质权登记编号'
				equityno = self.deal_dd_content(string,single)
				string = u'出质人'
				pledgor = self.deal_dd_content(string,single)
				string = u'出质人证照编号'
				pled_blicno = self.deal_dd_content(string,single)
				string = u'质权人'
				imporg = self.deal_dd_content(string,single)
				string = u"质权人证照编号"
				imporg_blicno = self.deal_dd_content(string,single)
				string = u"登记日期"
				equlle_date = self.deal_dd_content(string,single)
				string = u"出质状态"
				type = self.deal_dd_content(string,single)
				string = u"股权数额"
				impam = self.deal_dd_content(string, single)
				info[i] = [equityno,pledgor,pled_blicno,imporg,imporg_blicno,equlle_date,type,impam]
		else:
			flag = 100000004
		return info,flag
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, information,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		logging.info("stock total:%s" % total)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				equityno, pledgor, pled_blicno = information[key][0], information[key][1], information[key][2]
				imporg, imporg_blicno, equlle_date= information[key][3], information[key][4], information[key][5]
				type = information[key][6]
				impam = information[key][7]
				publicDate = '0000-00-00'
				count = cursor.execute(select_stock, (gs_basic_id, equityno))
				# print count

				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(stock_string, (
						gs_basic_id, equityno, pledgor, pled_blicno, impam, imporg, imporg_blicno, equlle_date,
						publicDate,type,updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					gs_stock_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					
					rows_count = cursor.execute(update_stock,
												(gs_basic_id, pledgor, pled_blicno, impam, imporg, imporg_blicno,
												 equlle_date,publicDate, type, updated_time, gs_stock_id))
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			print e
			remark = 100000006
			logging.error("stock error: %s" % e)
		finally:
			cursor.close()
			connect.close()
			flag = insert_flag + update_flag
			if remark < 100000001:
				remark = flag
				logging.info(" execute stock:%s" % remark)
			return remark, total, insert_flag, update_flag
def main(gs_py_id,gs_basic_id,url):
	Log().found_log(gs_py_id,gs_basic_id)
	name = 'stock'
	flag = Judge_status().judge(gs_basic_id, name, Stock, url)
	Judge_status().update_py(gs_py_id, update_stock_py, flag)
# if __name__ == '__main__':
#     main(gs_py_id,gs_basic_id,url)