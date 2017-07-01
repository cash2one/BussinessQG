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
    ge_share_url = get_url(config.gtshare_pattern,url_content)

    # print brand_url
    url["branch"] = branch_url
    url["shareholder"] = shareholder_url
    url["person"] = person_url
    url["change"] = change_url
    url["check"] = check_url
    url["permit"] = permit_url
    url["except"] = except_url
    url["punish"] = punish_url
    url["freeze"] = freeze_url
    url["stock"] = stock_url
    url["gt_permit"] = gt_permit_url
    url["brand"] = brand_url
    url["report"] = report_url
    url["mort"] = mort_url
    url["gtshare"] = gt_share_url

    return url


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
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["branch"], QGGS_branch, 'branch')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["person"], QGGS_person, 'person')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["change"], QGGS_change, 'change')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["shareholder"], QGGS_shareholder,'shareholder')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["check"], QGGS_check, 'check')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["punish"], QGGS_punish, 'punish')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["permit"], QGGS_permit, 'permit')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["gt_permit"], QGGS_permit, 'gt_permit')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["except"], QGGS_except, 'except')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["freeze"], QGGS_freeze, 'freeze')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["stock"], QGGS_stock, 'stock')
        # Get_BrancInfo().get_info(None, gs_basic_id, cursor, connect, url["brand"], QGGS_brand, 'brand')
        # Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url["mort"], QGGS_mort, 'mort')
        # update_report_main(information["report"], cursor, connect, gs_basic_id)
        Get_BranchInfo().get_info(None, gs_basic_id, cursor, connect, url["gtshare"], QGGS_gtshareholder, 'gtshare')
    else:
        logging.error('网页打开出错！！!')

# if __name__ == '__main__':
#     print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     start = time.time()
#     main()
#     print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
#
