#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_schange.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用于获取年报中的股权变更信息
from PublicCode import config
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Log
import hashlib
from PublicCode import deal_html_code
from lxml import etree
import logging
import time

schange_string = 'insert into gs_report_schange(gs_basic_id,gs_report_id,province,name,percent_pre,percent_after,dates,uuid,created,updated)values' \
                 '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

def name(url):
	headers = config.headers_detail
	content, status_code = Send_Request().send_request(url, headers)
	info = {}
	if status_code ==200:
		flag = 1
		result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
		dl = result.path("//div[@class= 'viewBox']/dl")[0]
		datallist = etree.tostring(dl).split('<dd style="border-bottom:1px solid #AE0000;padding-bottom:10px;">')
		datallist.remove(datallist[-1])
		for i, single in enumerate(datallist):
			single = etree.xpath(content, parser=etree.HTMLParser(encoding='utf-8'))
			string = u"股东"
			name = deal_dd_content(string,single)
			string = u"变更前"
			percent_pre = deal_dd_content(string,single)
			string = u"变更后"
			percent_after = deal_dd_content(string,single)
			string = u"变更日期"
			dates = deal_dd_content(string,single)
			info[i] = [name,percent_pre,percent_after,dates]
	else:
		flag = 100000004
	if flag ==1:
		deal_html_code.remove_repeat(info)
	return info,flag
	
	
	
# 用于处理dd标签中的内容
def deal_dd_content(string, result):
	dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
	dd = dd[0]
	data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
	return data


def update_to_db(gs_report_id, gs_basic_id,year, cursor, connect, information, province):
	insert_flag, update_flag = 0, 0
	remark = 0
	total = len(information)
	try:
		for key in information.keys():
			name, percent_pre, percent_after, dates = information[key][0], information[key][1], information[key][2], \
													  information[key][3]
			uuid = information[key][4]
			m = hashlib.md5()
			m.update(str(gs_basic_id) + str(year)+str(percent_pre)+str(percent_after)+str(dates)+str(name))
			uuid = m.hexdigest()
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			flag = cursor.execute(schange_string, (
				gs_basic_id, gs_report_id, province, name, percent_pre, percent_after, dates, uuid, updated_time,
				updated_time))
			connect.commit()
			insert_flag += flag
	
	except Exception, e:
		remark = 100000006
		logging.error('schange error %s' % e)
	finally:
		if remark < 100000001:
			remark = insert_flag
		return remark, total, insert_flag, update_flag