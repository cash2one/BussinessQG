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
from PublicCode.Public_code import Send_Request
from lxml import etree
import logging
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import random
import chardet
import linecache

# url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_bgxx_wap.dhtml?reg_bus_ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&clear=true'
# gs_basic_id = '1'
# gs_py_id = '1'
insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s and source =0 '
update_change_py = 'update gs_py set gs_py_id = %s,gs_change = %s,updated = %s where gs_py_id = %s'
headers = config.headers_detail
a = random.randrange(1, 1001)  # 1-9中生成随机数
# 从文件user-agent中对读取第a行的数据
theline = linecache.getline(r'user-agent.txt', a)
theline = theline.replace("\n", '')
headers["User-Agent"] = theline


class Change:
	def name(self, url):
		info = {}
		result = requests.get(url, headers=headers, timeout=5)
		status_code = result.status_code
		pattern = re.compile(u".*无查询结果.*|.*查询结果较多.*|.*访问异常.*")
		match = re.findall(pattern, result.content)
		if len(match) > 0 or chardet.detect(result.content)["encoding"] != 'utf-8':
			status_code = 404
		if status_code == 200:
			flag = 1
			cookies = result.cookies
			content = result.content
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			ddlist = result.xpath(".//dl/dd")
			for i, single in enumerate(ddlist):
				onclick = single.xpath("./@onclick")[0]
				if "alt_itemenName" in onclick:
					ddlist[i] = onclick.replace('window', 'zindow')
				else:
					ddlist[i] = onclick
			ddlist.sort()
			for i, single in enumerate(ddlist):
				pattern = re.compile(".*href='(.*?)'")
				# 匹配链接
				href = config.host + re.findall(pattern, single)[0]
				# time.sleep(0.5)
				self.deal_single_info(href, i, info, cookies)
		else:
			flag = 100000004
		return info, flag
	
	def deal_single_info(self, href, i, info, cookies):
		result = requests.get(href, headers=headers, cookies=cookies, timeout=5)
		status_code = result.status_code
		if status_code == 200:
			content = result.content
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			types = "变更"
			# 变更分为带表格的变更事项和不带表格的变更事项
			string = u'变更时间'
			plist = result.xpath(".//p[contains(.,'%s')]" % string)
			# 处理不带表格的信息
			if len(plist) == 0:
				ddlist = result.xpath(".//dl/dd/text()")
				change_date = deal_html_code.remove_symbol(ddlist[0])
				item = deal_html_code.remove_symbol(ddlist[1])
				content_before = deal_html_code.remove_symbol(ddlist[2])
				content_after = deal_html_code.remove_symbol(ddlist[3])
				info[i] = [types, change_date, item, content_before, content_after]
			
			elif len(plist) == 1:
				change_date, item, change_before, change_after = self.deal_table_info(result)
				info[i] = [types, change_date, item, change_before, change_after]
	
	# 用于处理带有表格的变更信息
	def deal_table_info(self, result):
		string = u'变更时间'
		plist = result.xpath(".//p[contains(.,'%s')]" % string)[0]
		item = plist.xpath("./following-sibling::*[1]")[0]
		change_date = deal_html_code.remove_symbol(plist.xpath("string(.)")).split(u"：")[-1]
		item = deal_html_code.remove_symbol(item.xpath("string(.)")).split(u"：")[-1]
		if u"投资人" in item:
			item = "投资人"
		elif u"认缴的出资额" in item:
			item = "投资人"
		elif u"实缴的出资额" in item:
			item = "投资人"
		string = u'变更前'
		change_before = self.deal_tr_content(result, string)
		string = u"变更后"
		change_after = self.deal_tr_content(result, string)
		return change_date, item, change_before, change_after
	
	# 用于对表格中tr的内容进行处理
	def deal_tr_content(self, result, string):
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
				string = string + "||" + text
		return string
	
	def update_to_db(self, info, gs_basic_id):
		HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
		connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
		insert_flag, update_flag = 0, 0
		flag = 0
		total = len(info)
		logging.info('change total:%s' % total)
		try:
			for key in info.keys():
				types, change_date = info[key][0], info[key][1]
				item, content_before, content_after = info[key][2], info[key][3], info[key][4]
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				count = cursor.execute(select_string, (gs_basic_id, item, change_date))
				if count == 0:
					source = 0
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
						source = 0
						row_count = cursor.execute(insert_string, (
							gs_basic_id, types, item, content_before, content_after, change_date, source, updated_time))
						insert_flag += row_count
						connect.commit()
		except Exception, e:
			print e
			flag = 100000006
			logging.error("change error :%s " % e)
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
				logging.info('execute change:%s' % flag)
			return flag, total, insert_flag, update_flag


def main(gs_search_id, gs_basic_id, url):
	Log().found_log(gs_search_id, gs_basic_id)
	name = 'change'
	flag = Judge_status().judge(gs_basic_id, name, Change, url)
