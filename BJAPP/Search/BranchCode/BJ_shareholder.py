#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_shareholder.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取发起人及出资信息

from PublicCode import config
from lxml import etree
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode.Public_code import Judge_status
import re
import logging
import time

# url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!view_tzr_wap.dhtml?reg_bus_ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&clear=true&fqr=fqr'
# gs_basic_id = '1'
# gs_py_id = '1'
share_string = 'insert into gs_shareholder(gs_basic_id,name,cate,types,license_type,license_code,iv_basic_id,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_shareholder_id from gs_shareholder where gs_basic_id = %s and name = %s and types = %s and cate = %s'
select_name = 'select gs_basic_id from gs_unique where name = "%s"'
update_share = 'update gs_shareholder set quit = 1 where gs_basic_id = %s and cate = 0'
update_quit = 'update gs_shareholder set quit = 0,updated = %s where gs_shareholder_id = %s and gs_basic_id = %s'
update_share_py = 'update gs_py set gs_py_id = %s,gs_shareholder = %s,updated = %s where gs_py_id = %s'


class Shareholder:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url, headers=config.headers_detail)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding="utf-8"))
			dlinfo = result.xpath("//div[@class ='viewBox']//dl")[0]
			dl = etree.tostring(dlinfo).split("<br/>")
			# 将最后一项的无用数据移除
			dl.remove(dl[-1])
			for i, single in enumerate(dl):
				single = etree.HTML(single, parser=etree.HTMLParser(encoding="utf-8"))
				name = deal_html_code.remove_symbol(single.xpath(".//dt")[0].xpath("string(.)"))
				templist = single.xpath('.//dd')
				types = deal_html_code.remove_symbol(templist[0].xpath("string(.)"))
				license_type = deal_html_code.remove_symbol(templist[1].xpath('string(.)'))
				license_code = deal_html_code.remove_symbol(templist[2].xpath('string(.)'))
				info[i] = [name, types, license_type, license_code]
		else:
			flag = 100000004
		return info, flag
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		cate = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			string = update_share % gs_basic_id
			cursor.execute(string)
			connect.commit()
			cursor.close()
			connect.close()
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				name, types, license_type, license_code = info[key][0], info[key][1], info[key][2], info[key][3]
				if name != '' or name != None:
					pattern = re.compile('.*公司.*|.*中心.*|.*集团.*|.*企业.*')
					result = re.findall(pattern, name)
					if len(result) == 0:
						iv_basic_id = 0
					else:
						select_unique = select_name % name
						number = cursor.execute(select_unique)
						if number == 0:
							iv_basic_id = 0
						elif int(number) == 1:
							iv_basic_id = cursor.fechall[0][0]
				else:
					iv_basic_id = 0
				count = cursor.execute(select_string, (gs_basic_id, name, types, cate))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(share_string, (
						gs_basic_id, name, cate, types, license_type, license_code, iv_basic_id, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					gs_shareholder_id = cursor.fetchall()[0][0]
					cursor.execute(update_quit, (updated_time, gs_shareholder_id, gs_basic_id))
					connect.commit()
		except Exception, e:
			remark = 100000006
			logging.info("shareholer error:%s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag


def main(gs_search_id, gs_basic_id, url):
	Log().found_log(gs_search_id, gs_basic_id)
	name = 'shareholder'
	flag = Judge_status().judge(gs_basic_id, name, Shareholder, url)
	
	# if __name__ == '__main__':
	#     main(gs_py_id,gs_basic_id,url)
