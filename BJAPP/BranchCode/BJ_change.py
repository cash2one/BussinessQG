#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_change.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 获取并更新变更信息
import re
import time
import requests
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from lxml import etree
import logging

url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_bgxx_wap.dhtml?reg_bus_ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&clear=true'
gs_basic_id = ''
insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s and source =0 '
class Change:
	def name(self,url):
		info = {}
		result = requests.get(url,headers = config.headers_detail,proxies = config.proxies)
		status_code = result.status_code
		if status_code ==200:
			content = result.content
			result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
			ddlist = result.xpath(".//dl/dd")
			for i,single in enumerate(ddlist):
				self.deal_single_info(url,i,info)
			print len(info)
		return info
				
	def deal_single_info(self,url,i,info):
		result = requests.get(url, headers=config.headers_detail,proxies = config.proxies)
		status_code = result.status_code
		cookies = result.cookies
		content = result.content
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		ddlist = result.xpath(".//dl/dd")[i]
		onclick = ddlist.xpath("./@onclick")[0]
		pattern = re.compile(".*href='(.*?)'")
		#匹配链接
		href = config.host + re.findall(pattern, onclick)[0]
		if status_code ==200:
			result = requests.get(href,headers = config.headers_detail,cookies = cookies,proxies = config.proxies)
			status_code = result.status_code
			if status_code==200:
				content = result.content
				result = etree.HTML(content,parser=etree.HTMLParser(encoding='utf-8'))
				types = "变更"
				#变更分为带表格的变更事项和不带表格的变更事项
				string = u'变更时间'
				plist = result.xpath(".//p[contains(.,'%s')]"%string)
				#处理不带表格的信息
				if len(plist) == 0:
					ddlist = result.xpath(".//dl/dd/text()")
					change_date = deal_html_code.remove_symbol(ddlist[0])
					item = deal_html_code.remove_symbol(ddlist[1])
					content_before= deal_html_code.remove_symbol(ddlist[2])
					content_after = deal_html_code.remove_symbol(ddlist[3])
					info[i] = [types,change_date,item,content_before,content_after]
					print types,change_date,item,content_before,content_after
				elif len(plist)==1:
					change_date, item, change_before, change_after = self.deal_table_info(result)
					info[i] = [types,change_date,item,change_before, change_after]
					print types,change_date,item,change_before, change_after
					
	#用于处理带有表格的变更信息
	def deal_table_info(self,result):
		string = u'变更时间'
		plist = result.xpath(".//p[contains(.,'%s')]" % string)[0]
		item = plist.xpath("./following-sibling::*[1]")[0]
		change_date = deal_html_code.remove_symbol(plist.xpath("string(.)")).split(u"：")[-1]
		item = deal_html_code.remove_symbol(item.xpath("string(.)")).split(u"：")[-1]
		string = u'变更前'
		change_before = self.deal_tr_content(result,string)
		string = u"变更后"
		change_after = self.deal_tr_content(result,string)
		return change_date,item,change_before,change_after
		
		
	#用于对表格中tr的内容进行处理
	def deal_tr_content(self,result,string):
		before_table = result.xpath(".//table[contains(.,'%s')]" % string)[0]
		trlist = before_table.xpath("./tr")
		trlist.remove(trlist[0])
		trlist.remove(trlist[0])
		string = ''
		for i, single in enumerate(trlist):
			temp = single.xpath("./td")
			text = deal_html_code.remove_symbol(temp[0].xpath("string(.)")) + " " + deal_html_code.remove_symbol(
				temp[1].xpath("string(.)"))
			if i == 0:
				string = string + text
			else:
				string = string + "\n" + text
		return string
	def update_to_db(self,info,gs_basic_id):
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		logging.info('change total:%s' % total)
		try:
			for key in info.keys():
				types,change_date = info[key][0],info[key][1]
				item, content_before, content_after = info[key][2],info[key][3],info[key][4]
				
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				count = cursor.execute(select_string, (gs_basic_id, item, change_date))
				if count == 0:
					source = 1
					row_count = cursor.execute(insert_string, (
						gs_basic_id, types, item, content_before, content_after, change_date, source, updated_time))
					insert_flag += row_count
					connect.commit()
				elif count >= 1:
					remark = 0
					for gs_basic_id, content in cursor.fetchall():
						if content == content_after:
							remark = 1
							break
					if remark == 0:
						row_count = cursor.execute(insert_string, (
							gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
						insert_flag += row_count
						connect.commit()
		except Exception, e:
			flag = 100000006
			logging.error("change error :%s " % e)
		finally:
			if flag < 100000001:
				flag = insert_flag
				logging.info('execute change:%s' % flag)
			return flag, total, insert_flag, update_flag
			
		
		
print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
start = time.time()
object = Change()
object.name(url)
print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)