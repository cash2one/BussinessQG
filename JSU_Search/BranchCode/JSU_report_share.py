#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_report_share.py
# @Author: Lmm
# @Date  : 2017-09-23
# @Desc  : 用于获得年报中的股东出资信息
from PublicCode import config

from PublicCode.Public_Code import GetBranchInfo
from PublicCode import deal_html_code
from PublicCode.Public_Code import Judge
import logging
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

share_string = 'insert into gs_report_share(gs_basic_id,gs_report_id,province,name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way,created,updated) values ' \
               '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

class Report_Share:
	#用于获取单页信息
	def deal_single_info(self, data, info):
		for i, singledata in enumerate(data):
			name = singledata["STOCK_NAME"]
			reg_amount = singledata["SHOULD_CAPI"]
			reg_amount = deal_html_code.match_float(reg_amount)
			reg_date = singledata["SHOULD_CAPI_DATE"]
			reg_date = deal_html_code.change_chinese_date(reg_date)
			reg_way = singledata["SHOULD_CAPI_TYPE"]
			ac_amount = singledata["REAL_CAPI"]
			ac_amount = deal_html_code.match_float(ac_amount)
			ac_date = singledata["REAL_CAPI_DATE"]
			ac_date = deal_html_code.change_chinese_date(ac_date)
			ac_way = singledata["REAL_CAPI_TYPE"]
			uuid = singledata["ID"]
			RN = singledata["RN"]
			info[RN] = [name, uuid,reg_amount, reg_date, reg_way, ac_amount, ac_date, ac_way]
	def update_to_db(self,gs_report_id,gs_basic_id,cursor,connect,info):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(info)
		try:
			for key in info.keys():
				name, uuid, reg_amount, reg_date = info[key][0], info[key][1], info[key][2], info[key][3]
				reg_way, ac_amount, ac_date, ac_way = info[key][4], info[key][5], info[key][6],info[key][7]
				
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				flag = cursor.execute(share_string, (
					gs_basic_id, gs_report_id, config.province, name, uuid, reg_amount, reg_date, reg_way, ac_amount, ac_date,
					ac_way, updated_time, updated_time))
				connect.commit()
				insert_flag += flag
		except Exception, e:
			remark = 100000006
			logging.error('share error %s' % e)
		finally:
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag
def main(report_id,gs_report_id,cursor,connect,gs_basic_id,org, id, seqid,regno):
	pattern = "report_share"
	types = config.key_params["report_share"]
	url = config.main_branch_url
	headers = config.headers
	object = Report_Share()
	info,flag = GetBranchInfo(url,headers,object,types).get_report_share_info(report_id,org, id, seqid,regno)
	flag = Judge().update_report_info(flag, info, gs_report_id, gs_basic_id, cursor, connect, pattern)
	