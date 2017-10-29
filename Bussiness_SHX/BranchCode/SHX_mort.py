#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_mort.py
# @Author: Lmm
# @Date  : 2017-10-19 10:43
# @Desc  : 用于获取页面中的动产抵押登记信息
import sys
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from lxml import etree
import logging
import hashlib
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

select_mort = 'select gs_mort_id from gs_mort where gs_basic_id = %s and code = %s'
mort_string = 'insert into gs_mort(gs_basic_id,id,code, dates, dept, amount, status,cates,period, ranges, remark,updated)' \
			  'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
update_mort = 'update gs_mort set gs_mort_id = %s ,dates = %s, dept = %s, amount = %s, status = %s,cates = %s,period = %s, ranges = %s, remark = %s,updated = %s ' \
			  'where gs_mort_id = %s'

select_goods = 'select gs_mort_goods_id from gs_mort_goods where gs_mort_id = %s and name = %s and ownership = %s and situation = %s'
goods_string = 'insert into gs_mort_goods(gs_mort_id,id,gs_basic_id,name,ownership,situation,remark,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
update_goods_sql = 'update gs_mort_goods set gs_mort_goods_id = %s,situation = %s,remark = %s,updated = %s where gs_mort_goods_id = %s'

select_person = 'select gs_mort_person_id from gs_mort_person where gs_mort_id = %s and name = %s'
person_string = 'insert into gs_mort_person(gs_mort_id,id,gs_basic_id,name,cert,number,updated) values (%s,%s,%s,%s,%s,%s,%s)'
update_mort_person = 'update gs_mort_person set gs_mort_person_id = %s,name = %s,cert = %s,updated = %s where gs_mort_person_id = %s'


class Mort:
	def __init__(self, pripid, url):
		self._pripid = pripid
		self._url = url
	
	# data.xpath("//table[@id = 'table_dcdy']//tr[@name='dcdy']")
	# 用于获取页面上的单条信息
	def get_info(self, data):
		info = {}
		tr_list = data.xpath(".//table[@id='table_dcdy']//tr[@name = 'dcdy']")
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0:
				continue
			
			temp["code"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			
			dates = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["dates"] = deal_html_code.change_date_style(dates)
			temp["dept"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["amount"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["status"] = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			
			onclick = td_list[6].xpath("./a/@onclick")[0]
			tuple = deal_html_code.match_key_content(str(onclick))
			xh = tuple[0]
			detail_url = self._url.format(self._pripid, xh)
			person_info, goods_info = self.get_detail_info(detail_url, temp)
			temp["person_info"] = person_info
			temp["goods_info"] = goods_info
			info[i] = temp
		return info
	
	# 用于打开详情页，获取担保概权信息，抵押人，抵押物信息
	def get_detail_info(self, detail_url, info):
		dict = {
			u"种类": "cates",
			u"范围": "ranges",
			u"期限": "period",
			u"备注": "remark",
		}
		headers = config.headers
		result, status_code = Send_Request().send_requests(detail_url, headers)
		if status_code == 200:
			data = etree.xpath(result, parser=etree.HTMLParser(encoding='utf-8'))
			string = u"被担保债权概况信息"
			table = data.xpath("//*[contains(.,'%s')]" % string)[0]
			for key, value in dict.iteritems():
				info[value] = deal_html_code.get_match_info(key, table)
			string = u"抵押权人概况信息"
			person_info = data.xpath("//*[contains(.,'%s')]" % string)[0]
			string = u"抵押权物概况信息"
			goods_info = data.xpath("//*[contains(.,'%s')]" % string)[0]
		else:
			info["cates"] = ''
			info["ranges"] = ''
			info["period"] = ''
			info["remark"] = ''
			person_info = {}
			goods_info = {}
		return person_info, goods_info
	
	# 抽取动产抵押物信息
	def get_goods_info(self, data):
		tr_list = data.xpath(".//tr[@name = 'dywgk']")
		info = {}
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			name = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["name"] = name
			ownership = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["ownership"] = ownership
			situation = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["situation"] = situation
			remark = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["remark"] = remark
			info[i] = temp
	
	# 抽取动产抵押人信息
	def get_person_info(self, data):
		tr_list = data.xpath(".//tr[@name = 'dydj']")
		info = {}
		for i, singledata in enumerate(tr_list):
			temp = {}
			td_list = singledata.xpath("./td")
			name = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["name"] = name
			cert = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["cert"] = cert
			number = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["number"] = number
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id):
		update_flag, insert_flag = 0, 0
		mort_flag = 0
		totalinfo = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, singledata in info.iteritems():
				value = singledata[0]
				code, dates, dept, amount = value["code"], value["dates"], value["dept"], value["amount"]
				status, cates, period, ranges, remark = value["status"], value["cates"], value["period"], value[
					"ranges"], \
														value["remark"]
				
				person_info = value["person_info"]
				goods_info = value["goods_info"]
				count = cursor.execute(select_mort, (gs_basic_id, code))
				if count == 0:
					m = hashlib.md5()
					m.update(code)
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(mort_string, (
						gs_basic_id, id, code, dates, dept, amount, status, cates, period, ranges, remark,
						updated_time))
					gs_mort_id = connect.insert_id()
					insert_flag += flag
					connect.commit()
				elif int(count) == 1:
					gs_mort_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(update_mort, (gs_mort_id,
														dates, dept, amount, status, cates, period, ranges, remark,
														updated_time, gs_mort_id))
					update_flag += flag
					connect.commit()
				self.update_goods(gs_mort_id, gs_basic_id, cursor, connect, goods_info)
				self.update_person(gs_mort_id, gs_basic_id, cursor, connect, person_info)
		except Exception, e:
			# print e
			logging.info('mort error :%s' % e)
			mort_flag = 100000006
		finally:
			cursor.close()
			connect.close()
			total = insert_flag + update_flag
			if mort_flag < 100000001:
				mort_flag = total
			return mort_flag, totalinfo, insert_flag, update_flag
	
	def update_goods(self, gs_mort_id, gs_basic_id, cursor, connect, info):
		total = len(info)
		
		logging.info('mort_goods :%s' % total)
		goods_flag = 0
		insert_flag, update_flag = 0, 0
		try:
			for key in info.keys():
				name, ownership, situation, remark = info[key][0], info[key][1], info[key][2], info[key][3]
				
				count = cursor.execute(select_goods, (gs_mort_id, name, ownership, situation))
				if count == 0:
					m = hashlib.md5()
					m.update(name + ownership)
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(goods_string, (
						gs_mort_id, id, gs_basic_id, name, ownership, situation, remark, updated_time))
					insert_flag += flag
					connect.commit()
				elif int(count) == 1:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					gs_mort_goods_id = cursor.fetchall()[0][0]
					flag = cursor.execute(update_goods_sql,
										  (gs_mort_goods_id, situation, remark, updated_time, gs_mort_goods_id))
					update_flag += flag
		except Exception, e:
			# print e
			goods_flag = 100000006
			logging.info('mort_goods error:%s' % e)
		finally:
			executetotal = insert_flag + update_flag
			if goods_flag < 100000001:
				goods_flag = executetotal
			logging.info('execute mort_goods :%s' % executetotal)
			return total, goods_flag
	
	# 更新抵押人信息
	def update_person(self, gs_mort_id, gs_basic_id, cursor, connect, info):
		total = len(info)
		logging.info('person_info :%s' % total)
		insert_flag, update_flag = 0, 0
		person_flag = 0
		try:
			for key in info.keys():
				name, cert, number = info[key][0], info[key][1], info[key][2]
				
				count = cursor.execute(select_person, (gs_mort_id, name))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					m = hashlib.md5()
					m.update(number)
					id = m.hexdigest()
					flag = cursor.execute(person_string,
										  (gs_mort_id, id, gs_basic_id, name, cert, number, updated_time))
					insert_flag += flag
					connect.commit()
				elif int(count) == 1:
					gs_mort_person_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					flag = cursor.execute(update_mort_person,
										  (gs_mort_person_id, name, cert, updated_time, gs_mort_person_id))
					update_flag += flag
					connect.commit()
		except Exception, e:
			# print e
			person_flag = 100000006
			logging.info('mort_person error:%s' % e)
		finally:
			executetotal = insert_flag + update_flag
			if person_flag < 100000001:
				person_flag = executetotal
				logging.info('execute mort_person:%s' % executetotal)
			return total, person_flag
