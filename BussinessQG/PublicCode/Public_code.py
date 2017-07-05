#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
import random
import time

import MySQLdb
import requests
import coutnumber
import re
# 用于连接数据库
class Connect_to_DB:
    def ConnectDB(self, HOST, USER, PASSWD, DB, PORT):
        "Connect MySQLdb and Print version."
        connect, cursor = None, None
        while True:
            try:
                connect = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB, port=PORT, charset='utf8')
                cursor = connect.cursor()
                logging.info("connect is success!")
                break
            except Exception, e:
                logging.error(e)
        return connect, cursor


# 用于发送请求
class Send_Request:
    def send_requests(self, url, num=10):
        list = []
        soup,status_code = None,None
        for i in range(0, 20):
            temp = random.randint(0, 9)
            list.append(temp)
        user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/%s%s%s.%s%s (KHTML, like Gecko) Chrome/%s%s.%s.%s%s%s%s.%s%s%s Safari/%s%s%s.%s%s\
            ' % (
            list[0], list[1], list[2], list[3], list[4], list[5], list[6], list[7], list[8], list[9], list[10],
            list[11],
            list[12], list[13], list[14], list[15], list[16], list[17], list[18], list[19])
        headersfirst = {
            "Host": "www.gsxt.gov.cn",
            "Proxy-Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # "Referer": "https://www.baidu.com/link?url=cxsFywBwbecQDgnYHggIMPkCYNCXq60XgQUeZdEpZgPfL-Rxw5mQNg45Q51fi_PN&wd=&eqid=a2e1675400237c41000000025949ce21",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8"
            # Cookie: __jsluid=e92eb3ffa9341978bd83a91256ed2744; UM_distinctid=15b7c2f3a9051-001ae4ee61beea-6e5c772b-100200-15b7c2f3a917af; Hm_lvt_d7682ab43891c68a00de46e9ce5b76aa=1497963057,1497963091,1497963094,1497966465; Hm_lpvt_d7682ab43891c68a00de46e9ce5b76aa=1497966465; LXB_REFER=www.baidu.com; tlb_cookie=45query_8080; CNZZDATA1261033118=1930934836-1492433574-http%253A%252F%252Fgsxt.saic.gov.cn%252F%7C1497963431; JSESSIONID=B64BDFDCDD7B035919CA0C12BFE78BE3-n2:3; Hm_lvt_cdb4bc83287f8c1282df45ed61c4eac9=1497966420,1497966423,1497966817,1497966917; Hm_lpvt_cdb4bc83287f8c1282df45ed61c4eac9=1497968045

        }
        header = headersfirst
        try:
            if num > 0:
                logging.info('there remains %s times to send requests ' % (num - 1))
                html = requests.get(url, headers=header, timeout=5)
                status_code = html.status_code
                logging.info('the status_code is %s ' % status_code)
                if status_code == 200:
                    soup = html.content
                    # soup = BeautifulSoup(html.content,"lxml")
        except Exception, e:
            print e
            logging.error(e)
            time.sleep(random.randint(0, 1))
            return self.send_requests(url, num=num - 1)

        if soup == None:
            logging.error('网站暂时无法访问！！!')
            return soup, status_code
        else:
            return soup, status_code


# 用于获得各个分页的内容
class Get_BranchInfo:
    def get_info(self, report_id, gs_basic_id, cursor, connect, url_pattern, QGGS_branch, name):
        total = 0
        # print url_pattern
        result, status_code = Send_Request().send_requests(url_pattern)
        pattern = re.compile(r'<html>.*</html>|.*index/invalidLink.*')
        pattern1 = re.compile(r'.*index/invalidLink.*')
        fail = re.findall(pattern,result)
        fail2 = re.findall(pattern1,result)
        if status_code == 200 and len(fail)==0:
            data = json.loads(result)["data"]
            recordsTotal = json.loads(result)["recordsTotal"]
            print "%s: %s" % (name, recordsTotal)
            if recordsTotal ==None:
                recordsTotal = 0
            coutnumber.counthtml[str(name)] = recordsTotal
            totalPage = json.loads(result)["totalPage"]
            perpage = json.loads(result)["perPage"]
            page = totalPage
            # print page

            if page == 1:
                information = QGGS_branch.name(data)
                if report_id == None:
                    flag = QGGS_branch.update_to_db(gs_basic_id, cursor, connect, information)
                else:
                    flag = QGGS_branch.update_to_db(report_id, gs_basic_id, cursor, connect, information)
                # print flag
                total += flag
            if page > 1:
                information = QGGS_branch.name(data)
                if report_id == None:
                    flag = QGGS_branch.update_to_db(gs_basic_id, cursor, connect, information)
                else:
                    flag = QGGS_branch.update_to_db(report_id, gs_basic_id, cursor, connect, information)
                # print flag
                total += flag
                for i in range(1, page):
                    start = perpage * i
                    url = url_pattern + '?start=%s' % start
                    # print url
                    result, status_code = Send_Request().send_requests(url)
                    data = json.loads(result)["data"]
                    information = QGGS_branch.name(data)
                    if report_id == None:
                        flag = QGGS_branch.update_to_db(gs_basic_id, cursor, connect, information)
                    else:
                        flag = QGGS_branch.update_to_db(report_id, gs_basic_id, cursor, connect, information)
                    # print flag
                    total += flag
            elif page == 0:
                logging.info('暂无 %s信息' % name)
        elif status_code == 404:
            logging.info('暂无 %s信息' % name)
        elif len(fail2) == 0:
            print '网页打开出错！！！'
            logging.info('网页打开出错！！！')
        else:
            logging.info('网页打开出错！！')
        print 'execute %s: %s' % (name, total)
        coutnumber.countexcute[str(name)] = int(total)
