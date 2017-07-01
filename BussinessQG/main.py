#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import re
import sys
import time

from bs4 import BeautifulSoup

import QGGS_basic
import QGGS_branch
import QGGS_change
import QGGS_check
import QGGS_except
import QGGS_freeze
import QGGS_permit
import QGGS_person
import QGGS_punish
import QGGS_shareholder
import QGGS_stock
import config
from  Public_code import Connect_to_DB as Connect_to_DB
from Public_code import Get_BranchInfo as Get_BrancInfo
from  Public_code import Send_Request as Send_Request

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

# host = 'http://www.gsxt.gov.cn'
host = config.host


# gs_basic_id = 123456


def get_url(pattern, url_content):
    url = re.findall(pattern, str(url_content))
    real_url = host + url[0]
    # print real_url
    return real_url


def get_singleinfo_url(result):
    information = {}
    url_content = BeautifulSoup(result, 'lxml').find("div", {"id": "url"}).find("script")
    # print url_content
    shareholder_url = get_url(config.shareholder_pattern, url_content)
    person_url = get_url(config.person_pattern, url_content)
    branch_url = get_url(config.branch_pattern, url_content)
    change_url = get_url(config.change_pattern, url_content)
    check_url = get_url(config.check_pattern, url_content)
    permit_url = get_url(config.permit_pattern, url_content)
    punish_url = get_url(config.punish_pattern, url_content)
    except_url = get_url(config.except_pattern, url_content)
    freeze_url = get_url(config.freeze_pattern, url_content)
    stock_url = get_url(config.stock_pattern, url_content)
    information["branch"] = branch_url
    information["shareholder"] = shareholder_url
    information["person"] = person_url
    information["change"] = change_url
    information["check"] = check_url
    information["permit"] = permit_url
    information["except"] = except_url
    information["punish"] = punish_url
    information["freeze"] = freeze_url
    information["stock"] = stock_url

    return information


def update_info_main():
    HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
    connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
    # code = ''
    # url = sys.argv[1]
    # gs_basic_id = sys.argv[2]
    url = 'http://www.gsxt.gov.cn/%7Bgf_U-l2ljEnz4D_mDTPCJYBF34TFvvA7C_B2LIkc4pNqH_eF6B_-D2Er3ZkFQE-DGE-wRVc1EPNgOBmKi7sh4vIIJqppCPWSvrjuyzxQ9rnaCU4UOn0PBzSUxB6YGKqcIoYQxdy-44VufagoTO0QPg-1498534746767%7D'
    gs_basic_id = 259
    result, status_code = Send_Request().send_requests(url)
    pattern = re.compile(".*返回首页.*")
    fail = re.findall(pattern, result)
    if status_code == 200 and len(fail) == 0:
        information = QGGS_basic.get_basic_info(result, status_code)
        QGGS_basic.update_basic(information, connect, cursor, gs_basic_id)
        information = get_singleinfo_url(result)
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["branch"], QGGS_branch, 'branch')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["person"], QGGS_person, 'person')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["change"], QGGS_change, 'change')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["shareholder"], QGGS_shareholder,
                                 'shareholder')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["check"], QGGS_check, 'check')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["punish"], QGGS_punish, 'punish')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["permit"], QGGS_permit, 'permit')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["except"], QGGS_except, 'except')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["freeze"], QGGS_freeze, 'freeze')
        Get_BrancInfo().get_info(gs_basic_id, cursor, connect, information["stock"], QGGS_stock, 'stock')
    else:
        print '网页打开出错！！!'
    connect.close()

# if __name__ == '__main__':
#     print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     start = time.time()
#     main()
#     print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
#
