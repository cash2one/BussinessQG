#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_punish.py
# @Author: Lmm
# @Date  : 2017-10-19 10:47
# @Desc  : 用于获取页面中的行政处罚信息
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from lxml import etree
from PublicCode.Public_code import Send_Request
import logging
import time
import hashlib

punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,name,pdfurl,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'
url = 'http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_xzcfxx&pripid={0}&random=1508721684203'
detail_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=xzfyDetail&maent.pripid={0}&maent.xh={1}&random=1508723649286 '


class Punish:
	def __init__(self, pripid, url):
		self._pripid = pripid
		self._url = url
	
	def get_info(self):
		url = self._url.format(self._pripid)
		headers = config.headers
		result, status_code = Send_Request().send_requests(url, headers)
		info = {}
		if status_code == 200:
			data = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
			tr_list = data.xpath("//table[@id = 'table_xzcf']//tr[@name = 'xzcf']")
			for i, singledata in enumerate(tr_list):
				temp = {}
				td_list = singledata.xpath("./td")
				temp["number"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
				temp["types"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
				temp["content"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
				temp["gov_dept"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
				date = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
				temp["date"] = deal_html_code.change_chinese_date(date)
				pub_date = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
				temp["pub_date"] = deal_html_code.change_chinese_date(pub_date)
				if len(tr_list) > 7:
					onclick = tr_list[7].xpath("./a[@onclick]")
					if len(onclick) == 0:
						tuple = deal_html_code.match_key_content(onclick[0])
						pripid = tuple[0]
						xh = tuple[1]
						pdfurl = detail_url.format(pripid, xh)
				else:
					pdfurl = ''
				temp["pdfutl"] = pdfurl
				temp["name"] = ''
			info[i] = temp
		return info
	
	def update_to_db(self, information, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in information.iteritems():
				number, types, content = value["number"], value["types"], value["content"]
				date, pub_date, gov_dept = value["date"], value["pub_date"], value["gov_dept"]
				name, pdfurl = value["name"], value["pdfurl"]
				count = cursor.execute(select_punish, (gs_basic_id, number))
				if count == 0:
					id = ''
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(punish_string, (
						gs_basic_id, id, number, types, content, date, pub_date, gov_dept, name, pdfurl, updated_time))
					insert_flag += rows_count
					connect.commit()
		
		except Exception, e:
			remark = 100000006
			logging.error("punish error:%s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
