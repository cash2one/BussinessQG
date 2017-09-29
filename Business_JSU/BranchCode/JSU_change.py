#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : JSU_change.py
# @Author: Lmm
# @Date  : 2017-09-21
# @Desc  : 用于获取网页中的变更信息，并将变更信息更新到数据库中
from PublicCode import  config

from PublicCode.Public_Code import Connect_to_DB
from PublicCode.Public_Code import Log
from PublicCode import  deal_html_code
from PublicCode.Public_Code import Judge

import time
import logging


#信息类型

gs_basic_id = 1
org = '8BD57D086433FE76407EBEB21C318A99'
id = 'C7F07915079BC570367524673937ED1A'
seqid = '22C72034011B36A98AF38569B13712C7'
regno = '3285999FF2A457319C9CD179CB18600EF75DDBF3D007D8DEEBA79BE855DED106'

types = config.key_params["change"]
insert_string = 'insert into gs_change(gs_basic_id,types,item,content_before,content_after,change_date,source,updated)values(%s,%s,%s,%s,%s,%s,%s,%s)'
select_string = 'select gs_basic_id,content_after from gs_change where gs_basic_id = %s and item = %s and change_date = %s and source =0'
update_change_py = 'update gs_py set gs_py_id = %s,gs_change = %s,updated = %s where gs_py_id = %s'
class Change:
	#用于处理单页信息
	def deal_single_info(self,data,info):
		for i,single in enumerate(data):
			content_before = single["OLD_CONTENT"]
			content_after = single["NEW_CONTENT"]
			change_date = single["CHANGE_DATE"]
			change_date = deal_html_code.change_chinese_date(change_date)
			item = single["CHANGE_ITEM_NAME"]
			#序号
			RN = single["RN"]
			info[RN] = [content_before, content_after, change_date, item]
	def update_to_db(self,info,gs_basic_id):
		insert_flag,update_flag = 0,0
		flag = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				content_before, content_after = info[key][0], info[key][1]
				change_date, item = info[key][2], info[key][3]
				types = '变更'
				updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
				count = cursor.execute(select_string,(gs_basic_id,item,change_date))
				if count == 0:
					source = 0
					row_count = cursor.execute(insert_string, (
								gs_basic_id, types, item, content_before, content_after, change_date,source,updated_time))
					insert_flag += row_count
					connect.commit()
				elif count >= 1:
					remark = 0
					for gs_basic_id, content in cursor.fetchall():
						if content == content_after:
							remark = 1
							break
					if remark == 0:
						row_count = cursor.execute(insert_string, (
							gs_basic_id, types, item, content_before, content_after, change_date, updated_time))
						insert_flag += row_count
						connect.commit()
		except Exception, e:
			flag = 100000006
			logging.error("change error :%s " % e)
		finally:
			cursor.close()
			connect.close()
			if flag < 100000001:
				flag = insert_flag
			return flag,total,insert_flag,update_flag
def main(org,id,seqid,regno,gs_basic_id,gs_py_id):
	pattern = "change"
	flag = Judge().update_info2(pattern, org, id, seqid, regno,Change, gs_basic_id)
	Judge().update_py(gs_py_id, update_change_py, flag)
	
# if __name__ == '__main__':
# 	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# 	start = time.time()
# 	main(org,id,seqid,regno)
# 	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
