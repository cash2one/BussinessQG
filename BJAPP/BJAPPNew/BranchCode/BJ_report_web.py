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
web_url = 'http://qyxy.baic.gov.cn/wapnb/wapnbAction!wapwz_bj.dhtml?entid=%s&cid=%s&pageNo=%s&pageSize=&clear='
def name(url):
	headers = config.headers_detail
	content, status_code = Send_Request().send_request(url, headers)
	info = {}
	if status_code ==200:
		flag = 1
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		dl = result.path("//div[@class= 'viewBox']/dl")[0]
		datallist = etree.tostring(dl).split('<dd style="border-bottom:1px solid #AE0000;padding-bottom:10px;word-wrap:break-word;">')
		datallist.remove(datallist[-1])
		datallist = list(set(datallist))
		if len(datallist)>0:
			pattern = re.compile(u".*共(.*?)页.*")
			number = re.findall(pattern, content)
			if len(number) == 1:
				totalpage = int(number[0])
			else:
				totalpage = 0
			if int(totalpage) == 1:
				j = 0
				deal_single_info(datallist, info, j)
			else:
				j = 0
				deal_single_info(datallist, info, j)
				entid = deal_html_code.match_entid(url)
				cid = deal_html_code.match_cid(url)
				href = web_url.format(entid, cid)
				for k in xrange(2, totalpage + 1):
					content, status_code = Send_Request().send_request(href,headers)
					if status_code == 200:
						start = k * 5 + 1
						result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
						dl = result.xpath("//div[@class='viewBox']/dl")[0]
						datalist = etree.tostring(dl).split(
							'<dd style="border-bottom:1px solid #AE0000;padding-bottom:10px;word-wrap:break-word;">')
						datalist = list(set(datalist))
						if len(datalist) > 0:
							datalist.remove(datalist[-1])
							deal_single_info(datalist, info, start)
					else:
						pass
	else:
		flag = 100000004
	info = deal_html_code.remove_repeat(info)
	return info,flag
#用于处理单条信息
def deal_single_info(datallist,info,j):
	for i, single in enumerate(datallist,j):
		single = etree.xpath(single, parser=etree.HTMLParser(encoding='utf-8'))
		string = u"类型"
		types = deal_dd_content(string, single)
		string = u"名称"
		name = deal_dd_content(string, single)
		string = u"网址"
		website = deal_dd_content(string, single)
		uuid = ''
		info[i] = [name, types, website, uuid]
	
# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data


def update_to_db( gs_report_id, gs_basic_id, year,cursor, connect, information, province):
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
				m.update(str(gs_basic_id) + str(year) +str(website))
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

