#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_punish.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获得行政处罚信息

from PublicCode import config
from PublicCode import deal_html_code
from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode.Public_Code import Judge

import logging
import time
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,name,pdfurl,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'
update_punish_py = 'update gs_py set gs_py_id = %s, gs_punish = %s ,updated = %s where gs_py_id = %s'

pdf_url = config.host+'/ecipplatform/manyCommonFnQueryServlet.json?showCrcontentPdf=true&org={0}&id={1}&seqId={2}'
class Punish:
	def deal_single_info(self,data,info):
		for i,singledata in enumerate(data):
			number = singledata["PEN_DEC_NO"]
			types = singledata["ILLEG_ACT_TYPE"]
			content = singledata["PEN_TYPE"]
			date = singledata["PUNISH_DATE"]
			date = deal_html_code.change_chinese_date(date)
			pub_date = singledata["CREATE_DATE"]
			pub_date = deal_html_code.change_chinese_date(pub_date)
			gov_dept = singledata["PUNISH_ORG_NAME"]
			punish_type = singledata["TYPE"]
			if types == None:
				types = singledata["PUNISH_CAUSE"]
			else:
				pass
			ID = singledata["ID"]
			ORG = singledata["ORG"]
			SEQ_ID = singledata["SEQ_ID"]
			if punish_type == '1':
				pdfurl = pdf_url.format(ORG,ID,SEQ_ID)
			else:
				pdfurl = ''
			name = ''
			RN = singledata["RN"]
		
			info[RN] = [number, types, content, date, pub_date, gov_dept, name, pdfurl]
	
	def update_to_db(self,  information,gs_basic_id):
		insert_flag, update_flag = 0, 0
		remark = 0
		total = len(information)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in information.keys():
				number, types, content = information[key][0], information[key][1], information[key][2]
				date, pub_date, gov_dept = information[key][3], information[key][4], information[key][5]
				name, pdfurl = information[key][6], information[key][7]
				count = cursor.execute(select_punish, (gs_basic_id, number))
				if count == 0:
					m = hashlib.md5()
					m.update(str(number))
					id = m.hexdigest()
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(punish_string, (
						gs_basic_id, id, number, types, content, date, pub_date, gov_dept, name, pdfurl, updated_time))
					insert_flag += rows_count
					connect.commit()
		
		except Exception, e:
			remark = 100000006
			logging.error("punish error:%s" % e)
		finally:
			cursor.close()
			connect.close()
			if remark < 100000001:
				remark = insert_flag
			return remark, total, insert_flag, update_flag


def main(org, id, seqid, regno, gs_basic_id):
	pattern = "punish"
	flag = Judge().update_info2(pattern, org, id, seqid, regno, Punish, gs_basic_id)



