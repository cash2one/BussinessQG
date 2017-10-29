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
from BranchCode import BJ_brand
from BranchCode import BJ_check
from BranchCode import BJ_change
from BranchCode import BJ_clear
from BranchCode import BJ_except
from BranchCode import BJ_freeze
from BranchCode import BJ_mort
from BranchCode import BJ_permit
from BranchCode import BJ_punish
from BranchCode import BJ_shareholder
from BranchCode import BJ_stock
from BranchCode import BJ_person
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# url = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_py_id = sys.argv[3]
url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!qy.dhtml?id=a1a1a1a02dc09576012dc127ca154f8e&scztdj=&credit_ticket=B18496E7FE543B5AC368563549155E6C'
gs_basic_id = 1118
gs_py_id = 2


def get_urllist(url):
	hreflist = {}
	result, status_code = Send_Request().send_request(url)
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
		get_basic_href(list, hreflist)
		get_good_info_href(list, hreflist)
		get_permit_href(list, hreflist)
		get_prompt_info_href(list, hreflist)
		get_warn_info_href(list, hreflist)
		get_self_pubilc_href(list, hreflist)
	
	else:
		flag = 100000004
	return hreflist, flag


# 用于获取基础信息包含的分支链接
def get_basic_href(result, hreflist):
	list = result.xpath('.//div[@id="categ_info_table_wz_0"]//div[@class="categ_info_02"]')
	for i, single in enumerate(list):
		string = u"发起人"
		list = single.xpath("./a[contains(text(),'%s')]" % string)
		if len(list) == 1:
			data = list[0]
			hreflist["shareholder"] = deal_html_code.match_href(data)
		else:
			string = u"出资历史信息"
			list = single.xpath("./a[contains(text(),'%s')]" % string)
			if len(list) == 1:
				data = list[0]
				hreflist["sharehistory"] = deal_html_code.match_href(data)
			else:
				string = u"变更登记信息"
				list = single.xpath("./a[contains(text(),'%s')]" % string)
				if len(list) == 1:
					data = list[0]
					hreflist["change"] = deal_html_code.match_href(data)
				else:
					string = u"清算信息"
					list = single.xpath("./a[contains(text(),'%s')]" % string)
					if len(list) == 1:
						data = list[0]
						hreflist["clear"] = deal_html_code.match_href(data)
					else:
						string = u"投资人"
						list = single.xpath("./a[contains(text(),'%s')]" % string)
						if len(list) == 1:
							data = list[0]
							hreflist["shareholder"] = deal_html_code.match_href(data)
						else:
							pass  # 保留代码，新增情况提供空间


# 用于获取许可资质包含的分支链接
def get_permit_href(result, hreflist):
	# string = "许可资质信息"
	info = []
	urllist = result.xpath("//div[@id='categ_info_table_wz_1']//div[@class='categ_info_02']/a")
	if len(urllist) == 0:
		logging.info("许可资质信息中无行政许可信息")
	else:
		for i, single in enumerate(urllist):
			href = deal_html_code.match_href(single)
			info.append(str(href))
		hreflist["permit"] = info


# 用于获取良好信息包含的分支链接
def get_good_info_href(result, hreflist):
	# string = "良好信息"
	info = []
	urllist = result.xpath("//div[@id='categ_info_table_wz_2']//div[@class='categ_info_02']")
	
	if len(urllist) == 0:
		logging.info("该企业中无良好信息")
	else:
		for i, single in enumerate(urllist):
			string = u"商标信息"
			list = single.xpath("./a[contains(text(),'%s')]" % string)
			if len(list) == 1:
				data = list[0]
				href = deal_html_code.match_href(data)
				info.append(str(href))
			else:
				pass
		if len(info) == 0:
			logging.info("该企业中无商标信息")
		else:
			hreflist["brand"] = info


# 用于获取提示信息包含的分支链接
def get_prompt_info_href(result, hreflist):
	# string = "提示信息"
	list = result.xpath('.//div[@id="categ_info_table_wz_3"]//div[@class="categ_info_02"]')
	if len(list) == 0:
		logging.info("无提示信息")
	else:
		checklist = []
		freezelist = []
		for i, single in enumerate(list):
			string = u"股权冻结信息"
			list = single.xpath("./a[contains(text(),'%s')]" % string)
			if len(list) == 1:
				data = list[0]
				href = deal_html_code.match_href(data)
				freezelist.append(str(href))
			else:
				string = u"股权质押"
				list = single.xpath("./a[contains(text(),'%s')]" % string)
				if len(list) == 1:
					data = list[0]
					hreflist["stock"] = str(deal_html_code.match_href(data))
				else:
					string = u"抽查信息"
					list = single.xpath("./a[contains(text(),'%s')]" % string)
					if len(list) == 1:
						data = list[0]
						href = deal_html_code.match_href(data)
						checklist.append(str(href))
					else:
						string = u"检查信息"
						list = single.xpath("./a[contains(text(),'%s')]" % string)
						if len(list) == 1:
							data = list[0]
							href = deal_html_code.match_href(data)
							checklist.append(str(href))
						else:
							string = u"股权解冻"
							list = single.xpath("./a[contains(text(),'%s')]" % string)
							if len(list) == 1:
								data = list[0]
								href = deal_html_code.match_href(data)
								freezelist.append(href)
							else:
								string = u"动产抵押"
								list = single.xpath("./a[contains(text(),'%s')]" % string)
								if len(list) == 1:
									data = list[0]
									hreflist["mort"] = str(deal_html_code.match_href(data))
		if len(checklist) == 0:
			logging.info("无抽查检查信息")
		else:
			hreflist["check"] = checklist
		if len(freezelist) == 0:
			logging.info("无冻结信息")
		else:
			hreflist["freeze"] = freezelist


# 用于获得警示信息中包含的分支链接
def get_warn_info_href(result, hreflist):
	list = result.xpath('.//div[@id="categ_info_table_wz_4"]//div[@class="categ_info_02"]')
	if len(list) == 0:
		logging.info("该企业无警示信息")
	else:
		for i, single in enumerate(list):
			string = u"行政处罚"
			list = single.xpath("./a[contains(text(),'%s')]" % string)
			if len(list) == 1:
				data = list[0]
				hreflist["punish"] = str(deal_html_code.match_href(data))
			else:
				string = u"异常名录"
				list = single.xpath("./a[contains(text(),'%s')]" % string)
				if len(list) == 1:
					data = list[0]
					hreflist["except"] = str(deal_html_code.match_href(data))
				else:
					pass  # 保留代码，为后期变动提供空间


# 用于获取企业自报信息中包含的分支链接
def get_self_pubilc_href(result, hreflist):
	# string = u"企业自报"
	string = u'年报'
	list = result.xpath(
		'.//div[@id="categ_info_table_wz_8"]//div[@class="categ_info_02"]/a[contains(text(),"%s")]' % string)
	if len(list) == 1:
		data = list[0]
		hreflist["report"] = deal_html_code.match_href(data)
	else:
		logging.info("该企业无年报信息")


def main():
	hreflist, flag = get_urllist(url)
	# print flag,hreflist
	# for key in hreflist:
	# 	print key,hreflist[key]
	print flag
	
	if flag == 1:
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
			BJ_branch.main(gs_py_id, gs_basic_id, branch_url)
		if "shareholder" in hreflist:
			share_url = hreflist["shareholder"]
			time.sleep(2)
			BJ_shareholder.main(gs_py_id, gs_basic_id, share_url)
		if "report" in hreflist:
			report_url = hreflist["report"]
		if "stock" in hreflist:
			stock_url = hreflist["stock"]
			time.sleep(2)
			BJ_stock.main(gs_py_id, gs_basic_id, stock_url)
		if "sharehistory" in hreflist:
			history_url = hreflist["sharehistory"]
		if "permit" in hreflist:
			permitlist = hreflist["permit"]
			BJ_permit.main(gs_py_id, gs_basic_id, permitlist)
		
		if "check" in hreflist:
			checklist = hreflist["check"]
			# print checklist
			for i, single in enumerate(checklist):
				href = single
				# print href
				time.sleep(2)
				BJ_check.main(gs_py_id, gs_basic_id, href)
		
		if "brand" in hreflist:
			brandlist = hreflist["brand"]
			for i, single in enumerate(brandlist):
				# print single
				time.sleep(2)
				BJ_brand.main(gs_py_id, gs_basic_id, single)
		
		if "clear" in hreflist:
			clear_url = hreflist["clear"]
			time.sleep(2)
			BJ_clear.main(gs_py_id, gs_basic_id, clear_url)
		if "except" in hreflist:
			except_url = hreflist["except"]
			time.sleep(2)
			BJ_except.main(gs_py_id, gs_basic_id, except_url)
		if "freeze" in hreflist:
			freezelist = hreflist["freeze"]
			for i, single in enumerate(freezelist):
				# print single
				time.sleep(2)
				BJ_freeze.main(gs_py_id, gs_basic_id, single)
		
		if "mort" in hreflist:
			mort_url = hreflist["mort"]
			time.sleep(1)
			BJ_mort.main(gs_py_id, gs_basic_id, mort_url)
		
		if "punish" in hreflist:
			punish_url = hreflist["punish"]
			# print punish_url
			time.sleep(2)
			BJ_punish.main(gs_py_id, gs_basic_id, punish_url)


if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main()
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
