#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_report_permit.py
# @Author: Lmm
# @Date  : 2017-09-09
# @Desc  : 用于获取年报中的行政许可信息
url = ''
import requests
from lxml import etree
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Judge_status
import time
import re
import logging

permit_string = 'insert into gs_report_permit(gs_basic_id,gs_report_id,uuid,province,types,valto,created,updated)' \
                'values(%s,%s,%s,%s,%s,%s,%s,%s)'
def name(url):
	content,status_code = Send_Request().send_request(url)
	info = {}
	if status_code ==200:
		flag = 1
		result = etree.HTML(content,parser=etree.HTMLParser(encoding="utf-8"))
		dl = result.xpath("//div[@class= 'viewBox']//dl")[0]
		datalist = etree.tostring(dl).split('<br/>')
		datalist.remove(datalist[-1])
		for i,single in enumerate(datalist):
			single = etree.HTML(single,parser=etree.HTMLParser(encoding="utf-8"))
			string = u"许可文件名称"
			types = deal_dd_content(string,single)
			string = u"有效期至"
			valto = deal_dd_content(string,single)
			uuid = ''
			info[i] = [types,valto,uuid]
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


def update_to_db( gs_report_id, gs_basic_id, cursor, connect, information, province):
	insert_flag, update_flag = 0, 0
	remark = 0
	total = len(information)
	try:
		for key in information.keys():
			types, valto, uuid = information[key][0], information[key][1], information[key][2]
			updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
			flag = cursor.execute(gs_basic_id, gs_report_id, uuid, province, types, valto, updated_time,
								  updated_time)
			insert_flag += flag
			connect.commit()
	except Exception, e:
		remark = 100000006
		logging("permit error %s" % e)
	finally:
		if remark < 100000001:
			remark = insert_flag
		return remark, total, insert_flag, update_flag
