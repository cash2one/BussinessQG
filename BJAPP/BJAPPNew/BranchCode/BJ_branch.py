#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : BJ_branch.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取北京信用分支机构信息并将信息插入到数据库中

from PublicCode import config
from PublicCode.Public_code import Log
from PublicCode import deal_html_code
from PublicCode.Public_code import Connect_to_DB
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Judge_status
from lxml import etree
import re
import hashlib
import time
import logging

url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!getEnt_Fzjgxx.dhtml?reg_bus_ent_id=CE37445CD0DC4B65B690D8FCBD5FE005&scztdj=&moreInfo=moreInfo&SelectPageSize=50&EntryPageNo=1&pageNo=1&pageSize=500&clear=true'
gs_basic_id = '229421869'
gs_py_id = 1
branch_string = 'insert into gs_branch(gs_basic_id,id,code,name,gov_dept,updated)values(%s,%s,%s,%s,%s,%s)'
select_string = 'select * from gs_branch where id = %s and gs_basic_id =%s'
update_branch_py = 'update gs_py set gs_py_id= %s, gs_branch = %s,updated = %s where gs_py_id = %s'


class Branch:
	# 用于获取网页信息
	def name(self, url):
		info = {}
		headers = config.headers_detail
		content, status_code = Send_Request().send_request(url, headers)
		if status_code == 200:
			flag = 1
			result = etree.HTML(content, parser=etree.HTMLParser(encoding='utf-8'))
			# total = result.xpath("//table[@id='tableIdStyle']//div/text()")[0]
			# pattern = re.compile(u".*记录总数(.*?)条.*")
			# number = re.findall(pattern,total)
			# if len(number)==1:
			# 	temp =int(number[0])
			trlist = result.xpath("//table[@id = 'tableIdStyle']//tr")
			for i, single in enumerate(trlist):
				tdlist = single.xpath("./td")
				if len(tdlist) == 0 or len(tdlist) < 4:
					pass
				else:
					name = deal_html_code.remove_symbol(tdlist[1].xpath("string(.)"))
					code = deal_html_code.remove_symbol(tdlist[2].xpath("string(.)"))
					gov_dept = deal_html_code.remove_symbol(tdlist[5].xpath("string(.)"))
					info[i] = [name, code, gov_dept]
		else:
			flag = 100000004
		return info, flag
	
	# 将获取到的数据插入到数据库中
	def update_to_db(self, info, gs_basic_id):
		insert_flag = 0
		update_flag = 0
		flag = 0
		total = len(info)
		try:
			HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
			connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
			for key in info.keys():
				name, code, gov_dept = info[key][0], info[key][1], info[key][2]
				m = hashlib.md5()
				m.update(str(gs_basic_id) + str(name))
				id = m.hexdigest()
				count = cursor.execute(select_string, (id, gs_basic_id))
				if count == 0:
					updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
					rows_count = cursor.execute(branch_string, (gs_basic_id, id, code, name, gov_dept, updated_time))
					insert_flag += rows_count
					connect.commit()
		except Exception, e:
			logging.info("update branch error:%s" % e)
			flag = 100000006
		finally:
			cursor.close()
			connect.close()
			
			if flag < 100000001:
				flag = insert_flag
			return flag, total, insert_flag, update_flag


def main(gs_py_id, gs_basic_id, url):
	Log().found_log(gs_py_id, gs_basic_id)
	name = 'branch'
	flag = Judge_status().judge(gs_basic_id, name, Branch, url)
	Judge_status().update_py(gs_py_id, update_branch_py, flag)

# if __name__ == '__main__':
#     main(gs_py_id,gs_basic_id,url)
