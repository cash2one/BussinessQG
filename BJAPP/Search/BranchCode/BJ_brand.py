#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_brand.py
# @Author: Lmm
# @Date  : 2017-09-08
# @Desc  : 用于获取商标信息
from lxml import etree
import logging
from PublicCode import deal_html_code
from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
import time
from PublicCode.Public_code import Judge_status
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

url = u'http://qyxy.baic.gov.cn/wap/creditWapAction!view_credit_wap.dhtml?categ_info=020034&ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&chr_id=26E74EE1E922002EE053D4000005002E,&info_categ_name=\u826f\u597d\u4fe1\u606f >> \u8457\u540d\u5546\u6807\u4fe1\u606f'
gs_basic_id = '229421869'
gs_py_id = '1'

brand_string = 'insert into ia_brand(gs_basic_id,ia_name,ia_zch,ia_type,updated)values(%s,%s,%s,%s,%s)'
select_brand = 'select ia_brand_id from ia_brand where ia_zch ="%s"'
update_brand = 'update ia_brand set ia_brand_id = %s,gs_basic_id = %s,ia_name = %s , ia_zch = %s ,ia_type = %s,updated = %s where ia_brand_id = %s'
update_brand_py = 'update gs_py set gs_py_id = %s ,gs_brand = %s,updated = %s where gs_py_id = %s'


class Brand:
	def name(self, url):
		info = {}
		content, status_code = Send_Request().send_request(url)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			dl = result.xpath('//div[@class= "viewBox"]//dl')[0]
			datalist = etree.tostring(dl).replace("<dl>", '').replace("</dl>", '').split(
				'<dd style="border-top:1px dashed #ccc;">')
			datalist.remove(datalist[-1])
			for i, single in enumerate(datalist):
				single = etree.HTML(single, parser=etree.HTMLParser(encoding='utf-8'))
				string = u'商标名称'
				ia_name = self.deal_dd_content(string, single)
				string = u'商标注册号'
				ia_zch = self.deal_dd_content(string, single)
				string = u'认定类别'
				ia_type = self.deal_dd_content(string, single)
				info[i] = [ia_name, ia_zch, ia_type]
			# print info
		else:
			flag = 100000004
		return info, flag
	
	# 用于处理dd标签中的内容
	def deal_dd_content(self, string, result):
		dd = result.xpath(".//dt[contains(.,'%s')]" % string)[0].xpath("./following-sibling::*[1]")
		dd = dd[0]
		data = deal_html_code.remove_symbol(dd.xpath("string(.)"))
		return data
	
	def update_to_db(self, info, gs_basic_id):
		insert_flag = 0
		update_flag = 0
		flag = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				ia_name, ia_zch, ia_type = info[key][0], info[key][1], info[key][2]
				select_string = select_brand % ia_zch
				# print select_string
				count = cursor.execute(select_string)
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(brand_string, (gs_basic_id, ia_name, ia_zch, ia_type, updated_time))
					insert_flag += rows_count
					connect.commit()
				elif count == 1:
					gs_brand_id = cursor.fetchall()[0][0]
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(update_brand,
												(gs_brand_id, gs_basic_id, ia_name, ia_zch, ia_type, updated_time,
												 gs_brand_id))
					update_flag += rows_count
					connect.commit()
		except Exception, e:
			logging.error("brand error:%s" % e)
			flag = 100000006
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = update_flag + insert_flag
			return flag, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'brand'
	flag = Judge_status().judge(gs_basic_id, name, Brand, url)

# if __name__ == '__main__':
#     main(gs_py_id,gs_basic_id)
