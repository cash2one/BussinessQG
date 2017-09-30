#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Get_Detail.py
# @Author: Lmm
# @Date  : 2017-09-06
# @Desc  : 用于获取详情信息的各部分链接
from PublicCode import config
import sys
from PublicCode import deal_html_code
from PublicCode.Public_code import Send_Request
import logging
from lxml import etree
from BranchCode import BJ_branch
from BranchCode import BJ_change
from BranchCode import BJ_shareholder
from BranchCode import BJ_person
from BranchCode import BJ_report
from BranchCode import BJ_share_history
import time
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id = sys.argv[3]
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!qy.dhtml?id=20e38b8c45c6dea10145d9d35ad233b7&scztdj=&credit_ticket=67CC9746BE3F356275C99F474D8F04A2'
gs_basic_id = 1990
gs_py_id = 2
def get_urllist(url):
	hreflist = {}
	result,status_code = Send_Request().send_request(url,headers=config.headers_detail)
	if status_code == 200:
		flag = 1
		id = deal_html_code.match_id(url)
		if u"分支机构" in result:
			hreflist["branch"] = str(config.branch_url.format(id))
		if u"主要人员" in result:
			hreflist["person"] = str(config.person_url.format(id))
		elif u"家庭成员" in result:
			hreflist["person"] = str(config.person_url.format(id))
		content = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
		list = content.xpath("//div[@class='viewBox']")[0]
		get_basic_href(list,hreflist)
		get_self_pubilc_href(list,hreflist)
	else:
		flag = 100000004
	return hreflist,flag

	
		
		
#用于获取基础信息包含的分支链接
def get_basic_href(result,hreflist):
	list = result.xpath('.//div[@id="categ_info_table_wz_0"]//div[@class="categ_info_02"]')
	for i,single in enumerate(list):
		string = u"发起人"
		list = single.xpath("./a[contains(text(),'%s')]"%string)
		if len(list) ==1:
			data = list[0]
			hreflist["shareholder"] = deal_html_code.match_href(data)
		else:
			string = u"出资历史信息"
			list = single.xpath("./a[contains(text(),'%s')]"%string)
			if len(list) ==1:
				data = list[0]
				hreflist["sharehistory"] = deal_html_code.match_href(data)
			else:
				string = u"变更登记信息"
				list = single.xpath("./a[contains(text(),'%s')]" % string)
				if len(list)==1:
					data = list[0]
					hreflist["change"] = deal_html_code.match_href(data)
				else:
					string = u"清算信息"
					list = single.xpath("./a[contains(text(),'%s')]" % string)
					if len(list)==1:
						data = list[0]
						hreflist["clear"] = deal_html_code.match_href(data)
					else:
						string = u"投资人"
						list = single.xpath("./a[contains(text(),'%s')]" % string)
						if len(list) == 1:
							data = list[0]
							hreflist["shareholder"] = deal_html_code.match_href(data)
						else:
							pass #保留代码，新增情况提供空间
#用于获取企业自报信息中包含的分支链接
def get_self_pubilc_href(result,hreflist):
	# string = u"企业自报"
	string = u'年报'
	list = result.xpath('.//div[@id="categ_info_table_wz_8"]//div[@class="categ_info_02"]/a[contains(text(),"%s")]'%string)
	if len(list)==1:
		data = list[0]
		hreflist["report"] = deal_html_code.match_href(data)
	else:
		logging.info("该企业无年报信息")
def main():

	hreflist,flag = get_urllist(url)
	print "flag:%s"%flag
	if flag ==1:
		if "change" in hreflist:
			change_url = hreflist["change"]
			# print change_url
			time.sleep(2)
			BJ_change.main(gs_py_id, gs_basic_id, change_url)
		if "person" in hreflist:
			person_url = hreflist["person"]
			BJ_person.main(gs_py_id, gs_basic_id, person_url)
			time.sleep(2)
		if "branch" in hreflist:
			branch_url = hreflist["branch"]
			# print branch_url
			time.sleep(2)
			BJ_branch.main(gs_py_id,gs_basic_id,branch_url)
		if "shareholder" in hreflist:
			share_url = hreflist["shareholder"]
			time.sleep(2)
			BJ_shareholder.main(gs_py_id,gs_basic_id,share_url)
			if "sharehistory" in hreflist:
				history_url = hreflist["sharehistory"]
				BJ_share_history.main(gs_py_id,gs_basic_id,history_url)
			else:
				pass
		if "report" in hreflist:
			
			report_url = hreflist["report"]
			print report_url
			BJ_report.main(gs_py_id,gs_basic_id,report_url)
			
			
if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)

	


