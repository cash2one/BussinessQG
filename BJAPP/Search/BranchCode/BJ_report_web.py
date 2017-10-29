#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_web.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用与获取年报中的网站或者网店信息
from PublicCode import config
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Log
from PublicCode.Public_code import Connect_to_DB
from PublicCode import deal_html_code
from lxml import etree
import logging
import time
import re
import hashlib

web_string = 'insert into gs_report_web(gs_basic_id,province,gs_report_id,name,types,website,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
web_url = 'http://qyxy.baic.gov.cn/wapnb/wapnbAction!wapwz_bj.dhtml?entid={0}&cid={1}&pageNo={2}&pageSize=&clear='


# url = ''
def name(url):
	headers = config.headers_detail
	content, status_code = Send_Request().send_request(url, headers)
	info = {}
	if status_code == 200:
		flag = 1
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		dl = result.xpath("//div[@class= 'viewBox']/dl")
		
		if len(dl) > 0:
			dl = dl[0]
			pattern = re.compile(u".*共(.*?)页.*")
			number = re.findall(pattern, content)
			if len(number) == 1:
				totalpage = int(number[0])
			else:
				totalpage = 0
			if int(totalpage) == 1:
				j = 0
				deal_single_info(dl, info, j)
			else:
				j = 0
				deal_single_info(dl, info, j)
				entid = deal_html_code.match_entid(url)
				cid = deal_html_code.match_cid(url)
				
				for k in xrange(2, totalpage + 1):
					href = web_url.format(entid, cid, k)
					content, status_code = Send_Request().send_request(href, headers)
					if status_code == 200:
						start = (k - 1) * 5 + 1
						result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
						dl = result.xpath("//div[@class='viewBox']/dl")[0]
						deal_single_info(dl, info, start)
					else:
						pass
	else:
		flag = 100000004
	info = deal_html_code.remove_repeat(info)
	return info, flag


# 用于处理单条信息
def deal_single_info(dl, info, j):
	namelist = dl.xpath("./dd")
	if len(namelist) > 1:
		namelist.remove(namelist[0])
		remark = j - 1
		for i, single in enumerate(namelist):
			if i % 3 == 0:
				remark += 1
				types = single.xpath("./text()")[0]
				types = deal_html_code.remove_space(types)
				info.setdefault(remark, []).append(types)
			elif i % 3 == 1:
				name = single.xpath("./text()")[0]
				name = deal_html_code.remove_space(name)
				info.setdefault(remark, []).append(name)
			elif i % 3 == 2:
				website = single.xpath("./text()")[0]
				website = deal_html_code.remove_space(website)
				info.setdefault(remark, []).append(website)
				uuid = ''
				info.setdefault(remark, []).append(uuid)
	
	else:
		pass


# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data


def update_to_db(gs_report_id, gs_basic_id, year, cursor, connect, information, province):
	insert_flag, update_flag = 0, 0
	remark = 0
	total = len(information)
	try:
		for key in information.keys():
			name, types, website = information[key][1], information[key][0], information[key][2]
			uuid = information[key][3]
			if name == '0' or website == '0' or name == '无' or website == '无':
				logging.info('网站信息为零')
			else:
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(year) + str(website))
				uuid = m.hexdigest()
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(web_string,
									  (gs_basic_id, province, gs_report_id, name, types, website, uuid, updated_time,
									   updated_time))
				connect.commit()
				insert_flag += flag
	except Exception, e:
		remark = 100000001
		logging.error('web error %s' % e)
	finally:
		if remark < 100000001:
			remark = insert_flag
		return remark, total, insert_flag, update_flag
