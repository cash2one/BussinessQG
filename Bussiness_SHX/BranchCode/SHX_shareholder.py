#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_shareholder.py
# @Author: Lmm
# @Date  : 2017-10-19 10:36
# @Desc  : 用于获取页面中的发起人及出资信息
#          股东信息有发起人及出资信息，投资人信息，合伙人信息
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from lxml import etree
import traceback
import logging
import time
import re

share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code,ra_date, ra_ways, true_amount,reg_amount,ta_ways,ta_date,iv_basic_id,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'

select_name = 'select gs_basic_id from gs_unique where name = "%s"'
update_share = 'update gs_shareholder set quit = 1 where gs_basic_id = %s and cate = 0'
update_quit = 'update gs_shareholder set quit = 0,updated = %s where gs_shareholder_id = %s and gs_basic_id = %s'


class Shareholder:
	def __init__(self, pripid, url):
		self._pripid = pripid
		self._url = url
	
	# 用于获得股东及出资信息
	# data.xpath("//table[@class= 'table_fr']")
	def get_info(self, data):
		info = {}
		for i, singledata in enumerate(data):
			
			td_list = singledata.xpath("./td")
			if len(td_list) == 0:
				continue
			
			self.deal_single_info(td_list, i, info)
		return info
	
	# 用于单条页面信息
	def deal_single_info(self, td_list, i, info):
		json_data = {
			"name": "",
			"types": "",
			"license_code": "",
			"license_type": "",
			"true_amount": "",
			"reg_amount": "",
			"ra_ways": "",
			"ra_date": "0000-00-00",
			"ta_ways": "",
			"ta_date": "0000-00-00"
		}
		# 如果是投资人，即包含两个字段
		
		if len(td_list) <= 2:
			
			name = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			types = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			json_data["name"] = name
			json_data["types"] = types
			json_data["license_code"] = ''
			json_data["license_type"] = ''
		else:
			# number = td_list[0].xpath("string(.)")
			
			name = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			json_data["name"] = name
			types = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			json_data["types"] = types
			license_type = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			json_data["license_type"] = license_type
			license_code = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			json_data["license_code"] = license_code
			detail = td_list[4].xpath("./a")
			# 如果长度为0证明是个假的详情，~-~即没有链接
			if len(detail) == 0:
				logging.info("该条信息无详情！")
			else:
				showRyxx = td_list[4].xpath("./a/@onclick")[0]
				key = deal_html_code.match_key_content(str(showRyxx))
				xh = key[0]
				pripid = key[1]
				isck = key[2]
				detail_url = self.url.format(xh, pripid, isck)
				self.deal_detail_info(detail_url)
		info[i] = json_data
	
	# 用于处理详情信息
	def deal_detail_info(self, detail_url, json_data):
		headers = config.headers
		result, status_code = Send_Request().send_requests(detail_url, headers)
		if status_code != 200:
			pass
		else:
			data = etree.xpath(result, pasert=etree.HTMLParser(encoding='utf-8'))
			string = u'实缴额'
			content = self.deal_td_content(string, data)
			json_data["true_amount"] = content
			string = u'认缴额'
			content = self.detail_url(string, data)
			json_data["reg_amount"] = content
			string = u"认缴明细信息"
			flag = 'rj'
			self.get_detail(string, data, json_data, flag)
			string = u"实缴明细信息"
			flag = 'sj'
			self.get_detail(string, data, json_data, flag)
	
	# 获得实缴出资额，认缴出资额
	def get_number(self, string, data):
		td = data.xpath("//*[contains(.,'%s')]" % string)[0].xpath(".//following-sibling::*[1]")
		content = td[0].xpath("string(.)")
		content = deal_html_code.remove_symbol(content)
		return content
	
	# 认缴明细信息，实缴明细信息
	def get_detail(self, string, data, json_data, flag):
		table = data.xpath("//*[contains(.,'%s')]" % string)[0].xpath(".//following-sibline::*[1]")
		td = table[0].xpath(".//td")
		if flag == 'rj':
			if len(td) < 3:
				logging.info("该条数据无认缴信息！")
				json_data["ra_ways"] = ''
				json_data["ra_date"] = '0000-00-00'
			else:
				ra_ways = deal_html_code.remove_symbol(td[0].xpath("string(.)"))
				ra_date = deal_html_code.remove_symbol(td[2].xpath("string(.)"))
				ra_date = deal_html_code.change_chinese_date(ra_date)
				json_data["ra_ways"] = ra_ways
				json_data["ra_date"] = ra_date
		elif flag == 'sj':
			if len(td) < 3:
				logging.info("该条数据无实缴信息！")
				json_data["ta_ways"] = ''
				json_data["ta_date"] = '0000-00-00'
			else:
				ta_ways = deal_html_code.remove_symbol(td[0].xpath("string(.)"))
				ta_date = deal_html_code.remove_symbol(td[2].xpath("string(.)"))
				ta_date = deal_html_code.change_chinese_date(ta_date)
				json_data["ta_ways"] = ta_ways
				json_data["ta_date"] = ta_date
	
	def update_to_db(self, info, gs_basic_id):
		
		cate = 0
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			string = update_share % gs_basic_id
			cursor.execute(string)
			connect.commit()
			cursor.close()
			connect.close()
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in info.items():
				name, license_code, license_type = value["name"], value["license_code"], value["license_type"]
				types, ra_date, ra_ways, true_amount = value["types"], value["ra_date"], value["ra_ways"], value[
					"true_amount"]
				reg_amount, ta_ways, ta_date = value["reg_amount"], value["ta_ways"], value["ta_date"]
				
				iv_basic_id = 0
				if name != '' and name != None:
					pattern = re.compile('.*公司.*|.*中心.*|.*集团.*|.*企业.*')
					result = re.findall(pattern, name)
					if len(result) == 0:
						iv_basic_id = 0
					else:
						select_unique = select_name % name
						number = cursor.execute(select_unique)
						if number == 0:
							iv_basic_id = 0
						elif int(number) == 1:
							iv_basic_id = cursor.fechall[0][0]
				else:
					iv_basic_id = 0
				
				count = cursor.execute(select_string, (gs_basic_id, name, types, cate))
				
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(share_string, (
						gs_basic_id, name, cate, types, license_type, license_code, ra_date, ra_ways, true_amount,
						reg_amount, ta_ways, ta_date, iv_basic_id, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					gs_shareholder_id = cursor.fetchall()[0][0]
					cursor.execute(update_quit, (updated_time, gs_shareholder_id, gs_basic_id))
					connect.commit()
		except Exception, e:
			traceback.format_exc()
			remark = 100000006
			logging.error("shareholder error:%s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
