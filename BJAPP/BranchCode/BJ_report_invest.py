#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_invest.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用与获取年报中的对外投资信息
from PublicCode import config
from PublicCode.Public_code import config
from PublicCode import deal_html_code
import requests
from lxml import etree
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Log
import logging
import time
import re
import hashlib
out_invest_string = 'insert into gs_report_invest(gs_basic_id,gs_report_id,province,name, code, ccode,uuid,created,updated) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
out_invest_url = 'http://qyxy.baic.gov.cn/wapnb/wapnbAction!wapdwtz_bj.dhtml?entid=%s&cid=%s&pageNo=%s&pageSize=&clear='
def name(url):
	content,status_code = Send_Request().send_request(url)
	if status_code == 200:
		flag = 1
		result = etree.xpath(content,parser=etree.HTMLParser(encoding='utf-8'))
		dl = result.xpath("//div[@class = viewBox']//dl")[0]
		info = {}
		if "企业名称" in content:
			datallist = etree.tostring(dl).split('<dd style="border-bottom:1px solid #AE0000;padding-bottom:10px;">')
			datallist.remove(datallist[-1])
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
				href = out_invest_url.format(entid, cid)
				for k in xrange(2, totalpage + 1):
					content, status_code = Send_Request().send_request(href)
					if status_code == 200:
						start = k * 5 + 1
						result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
						dl = result.xpath("//div[@class='viewBox']/dl")[0]
						datalist = etree.tostring(dl).split(
							'<dd style="border-bottom:1px solid #AE0000;padding-bottom:10px;">')
						datalist = list(set(datalist))
						if len(datalist) > 0:
							datalist.remove(datalist[-1])
							deal_single_info(datalist, info, start)
					else:
						pass
		else:
			flag = 100000004
		
	else:
		flag = 100000004
	if flag ==1:
		info = deal_html_code.remove_repeat(info)
	return info,flag
def deal_single_info(datallist,info,j):
	for i, single in enumerate(datallist,j):
		single = etree.xpath(single, parser=etree.HTMLParser(encoding='utf-8'))
		string = u"企业名称"
		name = deal_dd_content(string, single)
		if u"注册号" in single:
			string = u'注册号'
			code = deal_dd_content(string, single)
		else:
			code = ''
		if u"统一社会信用代码" in single:
			ccode = deal_html_code(string, single)
		else:
			ccode = ''
		info[i] = [name, code, ccode]
# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data
def update_to_db( gs_report_id, gs_basic_id,year, cursor, connect, information, province):
	insert_flag, update_flag = 0, 0
	remark = 0
	total = len(information)
	try:
		for key in information.keys():
			name = information[key][0]
			code = information[key][1]
			ccode = information[key][2]
			uuid = ''
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			flag = cursor.execute(out_invest_string, (
			gs_basic_id, gs_report_id, province, name, code, ccode, uuid, updated_time, updated_time))
			connect.commit()
			insert_flag += flag
	except Exception, e:
		remark = 100000006
		logging.error('invest error %s' % e)
	finally:
		if remark < 100000001:
			remark = insert_flag
		
		return remark, total, insert_flag, update_flag

