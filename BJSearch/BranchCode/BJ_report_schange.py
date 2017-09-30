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
		dl = result.xpath("//div[@class= 'viewBox']//dl")[0]
		ddlist = dl.xpath('./dd')
		remark =-1
		for i, single in enumerate(ddlist):
			if i % 4 ==0:
				remark+=1
				name = single.xpath("./text()")[0]
				name = deal_html_code.remove_space(name)
				info.setdefault(remark, []).append(name)
			elif i %4 ==1:
				percent_pre = single.xpath("./text()")[0]
				percent_pre = deal_html_code.remove_space(percent_pre)
				info.setdefault(remark, []).append(percent_pre)
			elif i%4 ==2:
				percent_after = single.xpath("./text()")[0]
				percent_after = deal_html_code.remove_space(percent_after)
				info.setdefault(remark, []).append(percent_after)
			elif i%4 ==3:
				dates = single.xpath("./text()")[0]
				dates = deal_html_code.remove_space(dates)
				info.setdefault(remark, []).append(dates)
				uuid = ''
				info.setdefault(remark,[]).append(uuid)
			
	else:
		flag = 100000004
	if flag ==1:
		deal_html_code.remove_repeat(info)
	return info,flag
	
	
def update_to_db(gs_report_id, gs_basic_id,year, cursor, connect, information, province):
	insert_flag, update_flag = 0, 0
	remark = 0
	total = len(information)
	try:
		for key in information.keys():
			name, percent_pre, percent_after, dates = information[key][0], information[key][1], information[key][2], \
													  information[key][3]
			
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