#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : SHX_stock.py
# @Author: Lmm
# @Date  : 2017-10-19 10:43
from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
import logging
import time

stock_string = 'insert into gs_stock(gs_basic_id,equityno,pledgor,pled_blicno,impam,imporg,imporg_blicno,equlle_date,public_date,type,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_stock = 'select gs_stock_id from gs_stock where gs_basic_id = %s and equityno = %s'
update_stock = 'update gs_stock set gs_basic_id = %s,pledgor = %s,pled_blicno = %s,impam = %s,imporg = %s,imporg_blicno = %s,equlle_date = %s,public_date = %s,type = %s ,updated = %s where gs_stock_id = %s'


class Stock:
	def __init__(self):
		pass
	
	# data.xpath("//table[@id = 'table_gqcz']//tr[@name='gqcz']")
	def get_info(self, data):
		info = {}
		for i, singledata in enumerate(data):
			temp = {}
			td_list = singledata.xpath("./td")
			if len(td_list) == 0:
				continue
			temp["equityNo"] = deal_html_code.remove_symbol(td_list[1].xpath("string(.)"))
			temp["pledgor"] = deal_html_code.remove_symbol(td_list[2].xpath("string(.)"))
			temp["pledBLicNo"] = deal_html_code.remove_symbol(td_list[3].xpath("string(.)"))
			temp["impAm"] = deal_html_code.remove_symbol(td_list[4].xpath("string(.)"))
			temp["impOrg"] = deal_html_code.remove_symbol(td_list[5].xpath("string(.)"))
			temp["impOrgBLicNo"] = deal_html_code.remove_symbol(td_list[6].xpath("string(.)"))
			equPleDate = deal_html_code.remove_symbol(td_list[7].xpath("string(.)"))
			temp["equPleDate"] = deal_html_code.change_chinese_date(equPleDate)
			publicDate = deal_html_code.remove_symbol(td_list[9].xpath("string(.)"))
			temp["type"] = deal_html_code.remove_symbol(td_list[8].xpath("string(.)"))
			temp["publicDate"] = deal_html_code.change_chinese_date(publicDate)
			info[i] = temp
		return info
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key, value in info.iteritems():
				equityNo, pledgor, pledBLicNo = value["equityNo"], value["pledgor"], value["pledBLicNo"]
				impAm, impOrg, impOrgBLicNo = value["impAm"], value["impOrg"], value["impOrgBLicNo"]
				equPleDate, publicDate, type = value["equPleDate"], value["publicDate"], value["type"]
				count = cursor.execute(select_stock, (gs_basic_id, equityNo))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(stock_string, (
						gs_basic_id, equityNo, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo, equPleDate, publicDate,
						type,
						updated_time))
					insert_flag += rows_count
					connect.commit()
				elif int(count) == 1:
					gs_stock_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					
					rows_count = cursor.execute(update_stock,
												(gs_basic_id, pledgor, pledBLicNo, impAm, impOrg, impOrgBLicNo,
												 equPleDate,
												 publicDate, type, updated_time, gs_stock_id))
					
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			cursor.close()
			connect.close()
			remark = 100000001
			
			logging.error("stock error: %s" % e)
		finally:
			flag = insert_flag + update_flag
			if remark < 100000001:
				remark = flag
			
			return remark, total, insert_flag, update_flag
