#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
import re
import sys
import time

from bs4 import BeautifulSoup

import QGGS_basic
import QGGS_branch
import QGGS_brand
import QGGS_change
import QGGS_check
import QGGS_except
import QGGS_freeze
import QGGS_mort
import QGGS_permit
import QGGS_person
import QGGS_punish
import QGGS_shareholder
import QGGS_stock
import config
from Public_code import Get_BranchInfo as Get_BrancInfo
from  Public_code import Send_Request as Send_Request
from QGGS_Report import *

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()

host = 'http://www.gsxt.gov.cn'
select_string = 'select gs_basic_id,uuid from gs_basic where code = %s'


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
    gt_permit_url = get_url(config.gt_permit, url_content)
    brand_url = get_url(config.brand_pattern, url_content)
    mort_url = get_url(config.mort_pattern, url_content)
    report_url = get_url(config.report_pattern, url_content)
    # print brand_url
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
    information["gt_permit"] = gt_permit_url
    information["brand"] = brand_url
    information["report"] = report_url
    information["mort"] = mort_url

    return information


def update_info_main(cursor, connect, code):
    cursor.execute(select_string, code)
    for basic_id, url in cursor.fetchall():
        gs_basic_id = basic_id
        url = url
    result, status_code = Send_Request().send_requests(url)
    pattern = re.compile(".*返回首页.*")
    fail = re.findall(pattern, result)
    if status_code == 200 and len(fail) == 0:
        information = QGGS_basic.get_basic_info(result, status_code)
        QGGS_basic.update_basic(information, connect, cursor, gs_basic_id)
        information = get_singleinfo_url(result)
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["branch"], QGGS_branch, 'branch')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["person"], QGGS_person, 'person')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["change"], QGGS_change, 'change')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["shareholder"], QGGS_shareholder,
                                 'shareholder')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["check"], QGGS_check, 'check')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["punish"], QGGS_punish, 'punish')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["permit"], QGGS_permit, 'permit')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["gt_permit"], QGGS_permit, 'gt_permit')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["except"], QGGS_except, 'except')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["freeze"], QGGS_freeze, 'freeze')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["stock"], QGGS_stock, 'stock')
        Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, information["brand"], QGGS_brand, 'brand')
        Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, information["mort"], QGGS_mort, 'mort')
        update_report_main(information["report"], cursor, connect, gs_basic_id)
    else:
        logging.error('网页打开出错！！!')

# if __name__ == '__main__':
#     print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     start = time.time()
#     main()
#     print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
#
