#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : config.py
# @Author: Lmm
# @Date  : 2017-09-05
# @Desc  :


#数据库配置-----------------------------------------
HOST, USER, PASSWD, DB, PORT = '127.0.0.1', 'root', '123456', 'test', 3306
#数据库配置-----------------------------------------

#日志保存路径Start-------------------------------------------------------------------------------
#log_path = './Public/Python'
log_path = '.'
#日志保存路径End---------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------
host = 'http://qyxy.baic.gov.cn'

list_url = 'http://qyxy.baic.gov.cn/wap/creditWapAction!QueryEnt20130412.dhtml?createTicket=B0418D3AFD2F24F19C3AA46E339B8744'
list_parmas = 'queryStr={0}&module=&idFlag=qyxy'
branch_url = 'http://qyxy.baic.gov.cn/xycx/queryCreditAction!getEnt_Fzjgxx.dhtml?reg_bus_ent_id={0}&moreInfo=moreInfo&SelectPageSize=50&EntryPageNo=1&pageNo=1&pageSize=500&clear=true'
person_url ='http://qyxy.baic.gov.cn/xycx/queryCreditAction!queryTzrxx_all.dhtml?reg_bus_ent_id={0}&moreInfo=&SelectPageSize=100&EntryPageNo=1&pageNo=1&pageSize=100&clear=true'

#列表请求头仿照
headers = {
"Host": "qyxy.baic.gov.cn",
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Content-Type": "application/x-www-form-urlencoded",
"Content-Length": "74",
"Referer": "http://qyxy.baic.gov.cn/wap",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1",

}
#详情请求头
headers_detail = {
"Host": "qyxy.baic.gov.cn",
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
"Accept-Encoding": "gzip, deflate",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1"
}
# 代理服务器-----------------------------------------------------------------------
proxyHost = "proxy.abuyun.com"
proxyPort = "9010"
#----------------------------------------------------------------------------------


# 代理隧道验证信息-----------------------------------------------------------------
proxyUser = "HQRMZT62299COJ2P"
proxyPass = "1B668ADB969075FD"

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
      "host": proxyHost,
      "port": proxyPort,
      "user": proxyUser,
      "pass": proxyPass,
    }

proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
}
#-------------------------------------------------------------------------------------------

#首页请求头
headers_index = {
"Host": "qyxy.baic.gov.cn",
"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
"Connection": "keep-alive",
"Cache-Control": "max-age=0",
"Upgrade-Insecure-Requests": "1",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Accept-Encoding": "gzip, deflate",
"Accept-Language": "zh-CN,zh;q=0.8"
}


#常用的User-Agent-------------------------------------------------------------------------------------------
USER_AGENTS = [
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
"Mozilla/5.0 (Linux; U; Android 4.1; en-us; GT-N7100 Build/JRO03C) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
"Mozilla/5.0 (Linux; U; Android 4.0; en-us; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
"Mozilla/5.0 (Linux; U; en-us; KFAPWI Build/JDQ39) AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.13 Safari/535.19 Silk-Accelerated=true",
"Mozilla/5.0 (Linux; U; Android 4.4.2; en-us; LGMS323 Build/KOT49I.MS32310c) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
"Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 550) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Mobile Safari/537.36 Edge/14.14263",
"Mozilla/5.0 (Linux; Android 4.3; Nexus 10 Build/JSS15Q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
"Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 4.3; Nexus 7 Build/JSS15Q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
"Mozilla/5.0 (MeeGo; NokiaN9) AppleWebKit/534.13 (KHTML, like Gecko) NokiaBrowser/8.5.0 Mobile Safari/534.13",
"Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Mobile Safari/537.36",
"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
"Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/555.63 (KHTML, like Gecko) Chrome/74.9.0592.391 Mobile Safari/922.39",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/206.66 (KHTML, like Gecko) Chrome/21.9.2678.264 Mobile Safari/510.93",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/259.22 (KHTML, like Gecko) Chrome/71.9.1957.868 Mobile Safari/893.42",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/579.29 (KHTML, like Gecko) Chrome/40.1.4475.845 Mobile Safari/351.69",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/734.25 (KHTML, like Gecko) Chrome/79.4.0183.594 Mobile Safari/821.78",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/381.18 (KHTML, like Gecko) Chrome/34.4.7280.272 Mobile Safari/791.10",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/184.84 (KHTML, like Gecko) Chrome/68.6.8715.694 Mobile Safari/192.64",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/082.85 (KHTML, like Gecko) Chrome/20.3.2259.159 Mobile Safari/713.29",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/604.35 (KHTML, like Gecko) Chrome/99.8.6218.390 Mobile Safari/406.17",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/228.47 (KHTML, like Gecko) Chrome/32.4.4558.561 Mobile Safari/137.74",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/605.95 (KHTML, like Gecko) Chrome/05.9.3954.488 Mobile Safari/080.20",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/740.53 (KHTML, like Gecko) Chrome/50.2.4868.954 Mobile Safari/499.33",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/833.57 (KHTML, like Gecko) Chrome/95.0.9861.276 Mobile Safari/471.69",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/539.81 (KHTML, like Gecko) Chrome/26.8.1088.628 Mobile Safari/347.00",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/397.53 (KHTML, like Gecko) Chrome/73.2.6948.952 Mobile Safari/372.51",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/176.36 (KHTML, like Gecko) Chrome/85.9.5713.061 Mobile Safari/149.42",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/122.50 (KHTML, like Gecko) Chrome/09.4.1736.297 Mobile Safari/215.38",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/806.06 (KHTML, like Gecko) Chrome/88.2.6932.110 Mobile Safari/015.77",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/944.57 (KHTML, like Gecko) Chrome/27.2.7924.857 Mobile Safari/365.22",
"Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/725.55 (KHTML, like Gecko) Chrome/43.9.5323.846 Mobile Safari/150.39",
]
#常用的User-Agent-------------------------------------------------------------------------------------------