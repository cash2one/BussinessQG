#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-10-18 14:47
# @Desc  : 用于一些固定的常用配置

#数据库配置Start--------------------------------------------------------------------------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库配置End----------------------------------------------------------------------------------------------------------

#日志路径Start----------------------------------------------------------------------------------------------------------
#log_path = './Public/Python'
log_path = '.'
#日志路径End------------------------------------------------------------------------------------------------------------
#省份Start--------------------------------------------------------------------------------------------------------------
province = 'SHX'
#省份End----------------------------------------------------------------------------------------------------------------

#链接Start--------------------------------------------------------------------------------------------------------------
url = 'http://sn.gsxt.gov.cn/ztxy.do?method=sslist&djjg=&random=1482506558083'
data = 'type=1&maent.entname={0}&pageNum={1}&currentPageNo=&pName=&BA_ZCH=&geetest_challenge=bb72a2c7d69515a92a2d75ff036128e33p&geetest_validate=337fc1a0f4329515d14f3c6579f5d4a4&geetest_seccode=337fc1a0f4329515d14f3c6579f5d4a4|7Cjordan'

jbxx_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_jcxx&pripid={0}&random=201608111029'
print_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=xxdy&random=1509005571739&pripid={0}&type={1}'
mort_detail_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=getdcdyDetail&maent.pripid={0}&maent.xh={1}&random=1508746591417'
freeze_detail_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=doSfxzDetail&maent.pripid={0}&lx={2}&maent.xh={1}&random=1508727658289'
share_detail_url = 'http://sn.gsxt.gov.cn/ztxy.do?method=frInfoDetail&maent.xh={0}&maent.pripid={1}&isck={2}&random=1508406673399'
#这一部分存的是需要用http才能获取到数据的链接或者某一部分的详情的链接
#行政许可，行政处罚，经营异常是这部分的链接，动产抵押，股权冻结，股东存的是详情链接
#企业自行公示的行政许可是详情链接,没有链接的自定义为空，方便以后改动
dict_url = {
	"branch": "",
	"brand": "",
	"change": "",
	"check": "",
	"clear": "",
	"stock": "",
	"punish2": "",
	"person": "",
	"permit": "http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_xzxkxx&pripid={0}&random=1509072058423",
	"punish": "http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_xzcfxx&pripid={0}&random=1508721684203",
	"except": "http://sn.gsxt.gov.cn/ztxy.do?method=qyinfo_jyycxx&pripid={0}&random=1508725286354",
	"mort": "http://sn.gsxt.gov.cn/ztxy.do?method=getdcdyDetail&maent.pripid={0}&maent.xh={1}&random=1508746591417",
	"freeze": "http://sn.gsxt.gov.cn/ztxy.do?method=doSfxzDetail&maent.pripid={0}&lx={2}&maent.xh={1}&random=1508727658289",
	"shareholder": "http://sn.gsxt.gov.cn/ztxy.do?method=frInfoDetail&maent.xh={0}&maent.pripid={1}&isck={2}&random=1508406673399",
	"permit2": "http://sn.gsxt.gov.cn/ztxy.do?method=xkxkDetail&maent.pripid={0}&maent.xh={1}&maent.lx={2}&random=1508487196751"
}

#链接End----------------------------------------------------------------------------------------------------------------

#基本信息项的字典Start----------------------------------------------------------------------------------------

info_dict = {
			u"注册号":"code",
			u"统一社会信用代码":"ccode",
			u"名称":"name",
			u"状态":"status",
			u"类型":"types",
			u"组成形式":"jj_type",
			u"法定代表人":"legal_person1",
			u"经营者":"runner",
			u"负责人":"responser",
			u"投资人":"investor",
			u"合伙人":"legal_person2",
			u"成立日期":"reg_date1",
			u"注册日期":"reg_date2",
			u"注册资":"reg_amount1",
			u"出资额":"reg_amount2",
			u"核准日期":"appr_date",
			u"期限自":"start_date",
			u"期限至":"end_date",
			u"登记机关":"reg_zone",
			u"住所":"reg_address1",
			u"场所":"reg_address2",
			u"地址":"reg_address3",
			u"范围":"scope"
		}

#基本信息项的字典End----------------------------------------------------------------------------------------
#年报分支信息Start------------------------------------------------------------------------------------------------------
report_dict = {
	u"社保信息":"report_lab",
	u"基本信息":"report_basic",
	u"担保信息":"report_assure",
	u"网站":"report_web",
	u"投资信息":"report_invest",
	u"资产状况":"report_run1",
	u"经营状况":"reoprt_run2",
	u"行政许可":"report_permit",
	u"股东及出资":"report_share"
}
#年报分支信息End--------------------------------------------------------------------------------------------------------
#年报基本信息字典字段Start------------------------------------------------------------------------------------------------------
report_basic_dict = {
	u"统一社会信用代码":'code',
	u"注册号":'ccode',
	u"企业名称":'name',
	u"地址":'address',
	u"编码":'postcode',
	u"电话":'tel',
	u"邮箱":'email',
	u"经营者":'runner',
	u"从业人数":'employee',
	u"女性从业人数":'womennum',
	u"状态":'status',
	u"控股":'holding',
	u"投资信息":'if_invest',
	u"网店":'if_website',
	u"担保信息":'if_fwarnnt',
	u"股权转让":'if_sharetrans',
	u"业务":'mainbus',
	u"注册资本":'amount'
}
#年报基本信息End--------------------------------------------------------------------------------------------------------

#年报中的社保信息字段对应Start--------------------------------------------------------------------------------------------------
report_lab_dict = {
	u"养老保险":"old_num",
	u"失业保险":"unemploy_num",
	u"医疗保险":"medical_num",
	u"工伤保险":"injury_num",
	u"生育保险":"birth_num",
	u"养老保险缴费基数":"old_base",
	u"失业保险缴费基数":"unemploy_base",
	u"基本医疗保险缴费基数":"medical_base",
	u"参加生育保险缴费基数":"birth_base",
	u"养老保险本期实际缴费金额":"old",
	u"失业保险本期实际缴费金额":"unemploy",
	u"医疗保险本期实际缴费金额":"medical",
	u"工伤保险本期实际缴费金额":"injury",
	u"生育保险本期实际缴费金额":"birth",
	u"养老保险累计欠缴金额":"old_owe",
	u"失业保险累计欠缴金额":"unemploy_owe",
	u"基本医疗保险累计欠缴金额":"medical_owe",
	u"工伤保险累计欠缴金额":"injury_owe",
	u"生育保险累计欠缴金额":"birth_owe"
}

#年报中的社保信息字段对应End------------------------------------------------------------------------------------------------------


#请求头仿照Start-----------------------------------------------------------------------------------------------------------------------
headers = {
"Host": "sn.gsxt.gov.cn",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Referer": "http://sn.gsxt.gov.cn/ztxy.do?method=index&random=1482483657466",
#"Cookie": "BSFIT_EXPIRATION=1482696558193; BSFIT_DEVICEID=NTg3Y-ttWCBfZjx7pflOKeLflb7W60HhYR756mKOGp-X99dh5doe1MmWbV4kuTw_PRBiXEVU7_B6YL6kMydHO0ppzqLaziXbWbzbw15mOgfTm_bKhDMV9LU0WR-giXvnSDHt4EBl2g_HVbT6_lSpzAsYc3Zzl5SY; BSFIT_OkLJUJ=FBBeKJyCVu53AsbYTRJDiEYVFnmO0x42; JSESSIONID=c0LSYcnpxzQGp10lLtFrL9tcWhPsVrgfpQJyGXwP85CGDPx7CzX4!-1311797943",
"Connection":"keep-alive",
"Upgrade-Insecure-Requests": "1",
"Content-Type": "application/x-www-form-urlencoded",
"Content-Length": "443"
}



#请求头仿照End-----------------------------------------------------------------------------------------------------------------------