#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @liangmengmeng
import random
import re
import sys
import os
#------------------------------------------------------------
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
#------------------------------------------------------------
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
#日志文件路径start-----------------------------------------------------------
#log_path = './Public/Python'
log_path = '.'
#日志文件路径end-------------------------------------------------------------

#网络主站start---------------------------------------------------------------
host = "http://www.gsxt.gov.cn"
#网络主站end----------------------------------------------------------------

#极验破解start
break_url = "http://59.110.138.116/geetest/get?token=seo_test1&reg=http://www.gsxt.gov.cn/SearchItemCaptcha"
search_url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
search_text = "tab=ent_tab&token=34911389&searchword=%s&geetest_challenge=%s&geetest_validate=%s&geetest_seccode=%s|7Cjordan"
#极验破解end

#数据库用户名配置-----------------------------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库用户名配置end--------------------------------------------------------


#人员图片与职位的对应start--------------------------------------------------
person_img = {
    'B0AAAAOCAYAAADT0Rc6AAABdklEQVR42qWUMUgDQRBFDwsrsbGw': "董事",
    'CsAAAAOCAYAAAC2POVFAAAB/0lEQVR42rWVQUSDYRjHJ5MOiUw6': "董事长",
    'B0AAAAOCAYAAADT0Rc6AAABaUlEQVR42mNgwA7SgNgUiV8OxEoM': "监事",
    'EcAAAAOCAYAAAB95wG7AAAC9UlEQVR42q2XT2RcURTGnxgR8WRT': '监事会主席',
    'DkAAAAOCAYAAACVZ7SQAAACrUlEQVR42q2WT2TcURDHn1irhwgV': '独立董事',
    'FUAAAAOCAYAAABevFBuAAACQklEQVR42s2YT0TDYRjHf5J0yMhk': '董事，董事长',
    'DkAAAAOCAYAAACVZ7SQAAACOUlEQVR42s2WQUTDURzHZzLJdEuS': '职工监事',
    'DkAAAAOCAYAAACVZ7SQAAACxklEQVR42qWWX2TbURTHfyr6MD+h': '外部监事',
    'EcAAAAOCAYAAAB95wG7AAACn0lEQVR42sWXT2RcURTGnxGRRYUa': '董事长，行长',
    'CsAAAAOCAYAAAC2POVFAAACPUlEQVR42sWVX2SVYRzHHzNHcsSR': '总经理',
    'DkAAAAOCAYAAACVZ7SQAAACk0lEQVR42rWWQWRcURSGn4roYoSI': '副董事长',
    'DkAAAAOCAYAAACVZ7SQAAACg0lEQVR42rWXQWScQRTHR0SsWqGH': '其他人员',
    'FUAAAAOCAYAAABevFBuAAAEC0lEQVR42r2YcUScYRzHXzknk8hk': '董事兼总经理',
    'DkAAAAOCAYAAACVZ7SQAAACk0lEQVR42rWWQWRcURSGn4roYoSI': '经理',
    'DkAAAAOCAYAAACVZ7SQAAACqElEQVR42r2WUYSUURTHx1irh8RK': '执行董事',
    'CsAAAAOCAYAAAC2POVFAAAB6klEQVR42p2VQUTDURzH/2bSYWKH': '负责人',
    'DkAAAAOCAYAAACVZ7SQAAACxUlEQVR42r2WX2RbURzHr4iYiRE1':'副总经理',
    'EcAAAAOCAYAAAB95wG7AAACn0lEQVR42sWXT2RcURTGnxGRRYUa':'董事，行长',
    'FUAAAAOCAYAAABevFBuAAADKklEQVR42sWXX2RbURzHIyL6EKVi':'董事，副行长',
    'B0AAAAOCAYAAADT0Rc6AAABoUlEQVR42r2UT0REURTGr5G0eCJJ':'经理',
    'CsAAAAOCAYAAAC2POVFAAAB00lEQVR42q2VMUgDMRSGi5TSoQil' :'副行长',
    'EcAAAAOCAYAAAB95wG7AAADcUlEQVR42r2Xb0TcYRzAf05O5kRm' :'董事兼经理'
}
#人员图片与职位对应end -----------------------------------------------------


#省份代号对应start ---------------------------------------------------------
province = {
    "10": "BEJ",
    "11": "BEJ",
    "12": "TJN",
    "13": "HEB",
    "14": "SXI",
    "15": "NMG",
    "21": "LNG",
    "22": "JLN",
    "23": "HLJ",
    "31": "SHH",
    "32": "JSU",
    "33": "ZHJ",
    "34": "ANH",
    "35": "FUJ",
    "36": "JXI",
    "37": "SHD",
    "41": "HEN",
    "42": "HUB",
    "43": "HUN",
    "44": "GAD",
    "45": "GXI",
    "46": "HAN",
    "50": "CHQ",
    "51": "SCH",
    "52": "GZH",
    "53": "YUN",
    "54": "XIZ",
    "61": "SHX",
    "62": "GSU",
    "63": "QNH",
    "64": "NXA",
    "65": "XNJ"
}
#省份代号对应end------------------------------------------------------------------



#各个分块数据url匹配对应----------------------------------------------------------
shareholder_pattern = re.compile(r'var shareholderUrl = "(.*?)"')
person_pattern = re.compile(r'var keyPersonUrl = "(.*?)"')
branch_pattern = re.compile(r'var branchUrl = "(.*?)"')
change_pattern = re.compile(r'var alterInfoUrl = "(.*?)"')
gtchange_pattern = re.compile('var gtAlertInfoUrl = "(.*?)"')
permit_pattern = re.compile(r'var otherLicenceInfoUrl = "(.*?)"')
check_pattern = re.compile(r'var spotCheckInfoUrl = "(.*?)"')
punish_pattern = re.compile(r'var punishmentDetailInfoUrl = "(.*?)"')
except_pattern = re.compile(r'var entBusExcepUrl = "(.*?)"')
freeze_pattern = re.compile(r'var judiciaryStockfreezePersonUrl = "(.*?)"')
stock_pattern = re.compile(r'var stakQualitInfoUrl = "(.*?)"')
gt_permit = re.compile(r'var insLicenceinfoUrl = "(.*?)"')
brand_pattern = re.compile(r'var trademarkInfoUrl = "(.*?)"')
report_pattern = re.compile(r'var anCheYearInfo = "(.*?)"')
mort_pattern = re.compile(r'var mortRegInfoUrl = "(.*?)"')
gtshare_pattern = re.compile('var insInvinfoUrl = "(.*?)"')
gtpunish_pattern = re.compile('var insPunishmentinfoUrl = "(.*?)"')
liquidation_pattern = re.compile('var liquidationUrl = "(.*?)"')
black_pattern = re.compile('var IllInfoUrl = "(.*?)"')

#各分块数据url---------------------------------------------------------------------------


#头部信息仿照start-----------------------------------------------------------------------
list = []

for i in range(0, 20):
    temp = random.randint(0, 9)
    list.append(temp)
user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/%s%s%s.%s%s (KHTML, like Gecko) Chrome/%s%s.%s.%s%s%s%s.%s%s%s Safari/%s%s%s.%s%s\
        ' % (
    list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10], list[11],
    list[12], list[13], list[14], list[15], list[16], list[17], list[18], list[19])

# 首页头部信息
headersfirst = {
    "Host": "www.gsxt.gov.cn",
    "Proxy-Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.baidu.com/link?url=cxsFywBwbecQDgnYHggIMPkCYNCXq60XgQUeZdEpZgPfL-Rxw5mQNg45Q51fi_PN&wd=&eqid=a2e1675400237c41000000025949ce21",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8"
    # Cookie: __jsluid=e92eb3ffa9341978bd83a91256ed2744; UM_distinctid=15b7c2f3a9051-001ae4ee61beea-6e5c772b-100200-15b7c2f3a917af; Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa=1497963057,1497963091,1497963094,1497966465; Hm_lpvt_d7682ab43891c68a00de46e9ce5b76aa=1497966465; LXB_REFER=www.baidu.com; tlb_cookie=45query_8080; CNZZDATA1261033118=1930934836-1492433574-http%253A%252F%252Fgsxt.saic.gov.cn%252F%7C1497963431; JSESSIONID=B64BDFDCDD7B035919CA0C12BFE78BE3-n2:3; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1497966420,1497966423,1497966817,1497966917; Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1497968045

}
# 搜索结果页面头部信息
headers = {
    "Host": "www.gsxt.gov.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    "ccept-Encoding": "gzip, deflate",
    "Content-Type": "application/x-www-form-urlencoded",
    "Content-Length": "214",
    "Referer": "http://www.gsxt.gov.cn/index.html",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}
#头部信息仿造end-------------------------------------------------------------------