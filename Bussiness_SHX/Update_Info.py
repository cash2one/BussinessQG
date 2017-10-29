#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Update_Info.py
# @Author: Lmm
# @Date  : 2017-10-18 16:38
# @Desc  : 用于更新数据，这次的代码改变了以前在存放信息时，以
#          i 作为键值对应一个列表，而是就i对应一个字典，及字典里面套字典
#          模仿公示系统里江苏，全国，四省等的json 结构（多个省代码整合的可以参考这种方式，
#          后面根据需要完善）
#          分支机构，人员，年报采集的是打印页的内容
#          在调用各部分模块信息的时候采用的是循环方式，虽然代码量减少了，但可读性不太好，调试起来也不太方便
#          另外各部分写成一个类没有什么非要写成类不可，也不是为了炫耀代码写的有多好，而是为了增加代码的扩展性
#          更高级的写法应该写成装饰器，这样代码就更容易扩展
import requests
from PublicCode import config
from PublicCode.Public_code import Send_Request
from PublicCode.Public_code import Log
from PublicCode import deal_html_code
from lxml import etree
from BranchCode import SHX_basic
from BranchCode import SHX_branch
from BranchCode import SHX_change
from BranchCode import SHX_check
from BranchCode import SHX_clear
from BranchCode import SHX_except
from BranchCode import SHX_freeze
from BranchCode import SHX_mort
from BranchCode import SHX_permit
from BranchCode import SHX_permit2
from BranchCode import SHX_punish
from BranchCode import SHX_punish2
from BranchCode import SHX_person
from BranchCode import SHX_report
from BranchCode import SHX_shareholder
from BranchCode import SHX_stock
from PublicCode.Public_code import Judge
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# uuid = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_search_id = sys.argv[3]
url = 'http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_jcxx&pripid={0}&random=201608111029'
print_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=xxdy&random=1509005571739&pripid={0}&type={1}'

uuid = '28890||1'
gs_basic_id = 1
gs_search_id = 1

# 要获取的信息对象
dict = {
	u"营业执照信息": "basic",
	u"股东及出资信息": "shareholder1",
	u"发起人": "shareholder2",
	u"投资人": "shareholder3",
	u"变更信息": "change",
	u"清算信息": "clear",
	u"动产抵押登记信息": "mort",
	u"司法协助信息": "freeze",
	u"股权出质登记信息": "stock",
	u"行政许可信息": "permit2",
	u"行政处罚信息": "punish2",
	u"年报信息": "report",
	
}
# 类的对象字典，
class_dict = {
	"basic": SHX_basic.Basic,
	"change": SHX_change.Change,
	"check": SHX_check.Check,
	"clear": SHX_clear.Clear,
	"freeze": SHX_freeze.Freeze,
	"mort": SHX_mort.Mort,
	"permit": SHX_permit.Permit,
	"permit2": SHX_permit2.Permit,
	"person": SHX_person.Person,
	"punish": SHX_punish.Punish,
	"punish2": SHX_punish2.Punish,
	# "report":SHX_report.Report,
	"shareholder": SHX_shareholder.Shareholder,
	"stock": SHX_stock.Stock,
	"branch": SHX_branch.Branch,
	"person": SHX_person.Person,
	"except": SHX_except.Except
}


def get_key(uuid):
	list = uuid.split("||")
	pripid = list[0]
	types = list[1]
	return pripid, types


def get_html_data(url, print_url):
	headers = config.headers
	info = {}
	result, status_code = Send_Request().send_requests(url, headers)
	if status_code == 200:
		data = etree.HTML(result, parser=etree.HTMLParser(encoding='utf-8'))
		for key, value in dict.iteritems():
			info[value] = deal_html_code.match_info(key, data)
		if info["shareholder1"] != '':
			info["shareholder"] = info["shareholder1"]
		elif info["shareholder2"] != '':
			info["shareholder"] = info["shareholder2"]
		elif info["shareholder3"] != '':
			info["shareholder"] = info["shareholder3"]
		# 最后删除不要的键值，以防下面循环去键值对应信息时出错
		del info["shareholder1"]
		del info["shareholder2"]
		del info["shareholder3"]
	else:
		print '获取基本信息失败！'
	print_info, status_code = Send_Request().send_requests(print_url, headers)
	if status_code == 200:
		print_data = etree.HTML(print_info, parser=etree.HTMLParser(encoding='utf-8'))
		string = u'人员信息'
		info["person"] = deal_html_code.match_info(string, print_data)
		
		if info["person"] == '':
			string = u'成员信息'
			info["person"] = deal_html_code.match_info(string, print_data)
		string = '分支机构'
		info["branch"] = deal_html_code.match_info(string, print_data)
		# 将整个打印页的内容先赋值给info["report],传递给Report类，report类根据年份查找对应年份的信息
		info["report"] = print_data
	
	return info


# 一次性对所有的信息进行更新
def get_all_info(gs_basic_id, gs_search_id, info_list):
	Log().found_log(gs_basic_id, gs_search_id)
	# info = class_dict["basic"]().get_info(info_list["basic"])
	# flag = class_dict["basic"]().update_to_db(info,gs_basic_id)
	# print "basic:%s"%flag
	pripid = '28890'
	name = '西安银行股份有限公司'
	
	for key, value in info_list.iteritems():
		# 这两块信息较为特殊，拿出来单独处理
		if key == "basic" or key == "report":
			continue
		
		if key not in info_list.keys():
			continue
		Judge(pripid, name, config.dict_url[key]).update_info(key, class_dict[key], value, gs_basic_id)


# uuid，gs_search_id,gs_search_id,gs_basic_id在这里是php传递的，是全局变量
# 按照参数的方式进行传递时也是为了增加代码的扩展性
# 比如有一天php不传递参数了，参数是从另外一份代码传递的，这样只需进到这个借口，而不需改变代码结构

def main(uuid, gs_search_id, gs_basic_id):
	pripid, types = get_key(uuid)
	url = config.jbxx_url.format(pripid)
	print_url = config.print_url.format(pripid, types)
	info_list = get_html_data(url, print_url)
	get_all_info(gs_basic_id, gs_search_id, info_list)


if __name__ == '__main__':
	print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	start = time.time()
	main(uuid, gs_search_id, gs_basic_id)
	print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
