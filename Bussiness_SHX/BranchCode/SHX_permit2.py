#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_permit2.py
# @Author: Lmm
# @Date  : 2017-10-19 10:45
# @Desc  : 用于获取企业自行公示的行政许可信息
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode import deal_html_code
import logging
import time
from lxml import etree

select_string = 'select gs_permit_id from gs_permit where gs_basic_id = %s and filename = %s and code = %s and start_date = %s and end_date = %s and source = 1'
permit_string = 'insert into gs_permit(gs_basic_id,id,name, code, filename, start_date, end_date, content, gov_dept,status,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_permit_py = 'update gs_py set gs_py_id = %s ,gs_permit = %s ,updated = %s where gs_py_id = %s'
permit_alter = 'insert into gs_permit_alter(gs_permit_id,alt_name, alt_date, alt_af, alt_be,updated) values(%s,%s,%s,%s,%s,%s)'
select_permit =  'select gs_permit_alter_id from gs_permit_alter where gs_permit_id = %s and alt_name = %s and alt_date = %s'



class Permit:
	def __init__(self,pripid,url):
		self._pripid = pripid
		self._url = url
	
	#data.xpath("//table[@id = 'xzxk']")
	def get_info(self,data):
		tr_list = data.xpath(".//tr[@name = 'xzxk']")
		info = {}
		for i,singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			# number = deal_html_code.remove_symbol(td_list[0].xpath("string(.)"))
			temp["name"] = ''
			temp["code"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["filename"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			start_date = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["start_date"] = deal_html_code.change_chinese_date(start_date)
			end_date = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["end_date"] = deal_html_code.change_chinese_date(end_date)
			temp["gov_dept"] = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			temp["content"] = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
			temp["status"] = deal_html_code.remove_symbol(td_list[7].xpath("string(.)"))
			onclick = td_list[8].xpath("./a/@onclick")
			if len(onclick) ==0:
				logging.info("该条信息无详情信息！")
			else:
				onclick = onclick[0]
				tuple = deal_html_code.match_key_content(str(onclick))
				pripid = tuple[0]
				xh = tuple[1]
				lx = tuple[2]
				detail_url = self._url.format(pripid,xh,lx)
				self.get_detail_info(detail_url)
			info[i] = temp
		return info
	
	def get_detail_info(self, url):
		result, status_code = Send_Request().send_requests(url)
		info = {}
		if status_code == 200:
			data = etree.xpath(result,parser = etree.HTMLParser(encoding='utf-8'))
			if len(data) == 0:
				logging.info("暂无permit详情信息")
			else:
				tr_list = data.xpath("//tr[@name='xzxkbg']")
				for i, singledata in enumerate(tr_list):
					td_list = singledata.xpath("./td")
					alt_name = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
					alt_date = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
					alt_date = deal_html_code.change_date_style(alt_date)
					alt_af = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
					alt_be = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
					info[i] = [alt_name, alt_date, alt_af, alt_be]
		return info
	
	def update_detail_info(self, info, cursor, connect, gs_permit_id):
		try:
			for key,value in info.keys():
				alt_name, alt_date, alt_af, alt_be = info[key][0], info[key][1], info[key][2], info[key][3]
				count = cursor.execute(select_permit, (gs_permit_id, alt_name, alt_date))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					cursor.execute(permit_alter, (gs_permit_id, alt_name, alt_date, alt_af, alt_be, updated_time))
					connect.commit()
		except Exception, e:
			logging.error("permit detail error:%s" % e)
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		source = 0
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key,value in info.iteritems():
				name, code, filename, start_date = value["name"], value["code"], value["filename"], value["start_date"]
				end_date, content, gov_dept = value["end_date"], value["content"], value["gov_dept"]
				status = value["status"]
				count = cursor.execute(select_string, (gs_basic_id, filename, code, start_date, end_date))
				id = ''
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(permit_string, (
						gs_basic_id, id, name, code, filename, start_date, end_date, content, gov_dept, status, source,
						updated_time))
					insert_flag += rows_count
					connect.commit()
		
		except Exception, e:
			cursor.close()
			connect.close()
			remark = 100000006
			logging.error("permit error: %s" % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag