#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : QG_Update.py
# @Author: Lmm
# @Date  : 2017-10-13
# @Desc  :

from PublicCode import config
from PublicCode.Public_code import Send_Request
from bs4 import BeautifulSoup
import re
import logging
from BranchCode import QGGS_basic
from BranchCode import QGGS_branch
from BranchCode import QGGS_black
from BranchCode import QGGS_brand
from BranchCode import QGGS_change
from BranchCode import QGGS_check
from BranchCode import QGGS_clear
from BranchCode import QGGS_except
from BranchCode import QGGS_freeze
from BranchCode import QGGS_mort
from BranchCode import QGGS_permit
from BranchCode import QGGS_permit2
from BranchCode import QGGS_person
from BranchCode import QGGS_punish
from BranchCode import QGGS_punish2
from BranchCode import QGGS_shareholder
from BranchCode import QGGS_stock
from BranchCode import QGGS_report




#调用各部分信息的 函数，进行整体性更新
def update_all_info(url, gs_basic_id):
    result, status_code = Send_Request().send_requests(url)
    pattern = re.compile(".*返回首页.*")
    fail = re.findall(pattern, result)
    if status_code == 200 and len(fail) == 0:
        urllist,flag = QGGS_basic.main(url,gs_basic_id)
        if flag <100000001:
            QGGS_black.main(gs_basic_id, urllist["black"])
            QGGS_branch.main(gs_basic_id, urllist["branch"])
            QGGS_brand.main(gs_basic_id, urllist["brand"])
            QGGS_change.main(gs_basic_id, urllist["change"])
            QGGS_change.main(gs_basic_id, urllist["change2"])
            QGGS_check.main(gs_basic_id, urllist["check"])
            QGGS_clear.main(gs_basic_id, urllist["clear"])
            QGGS_except.main(gs_basic_id, urllist["except"])
            QGGS_freeze.main(gs_basic_id, urllist["freeze"])
            QGGS_mort.main(gs_basic_id, urllist["mort"])
            QGGS_permit.main(gs_basic_id, urllist["permit"])
            QGGS_permit2.main(gs_basic_id, urllist["permit2"])
            QGGS_person.main(gs_basic_id, urllist["person"])
            QGGS_punish.main(gs_basic_id, urllist["punish"])
            QGGS_punish2.main(gs_basic_id, urllist["punish2"])
            QGGS_shareholder.main(gs_basic_id, urllist["shareholder"])
            QGGS_stock.main(gs_basic_id, urllist["stock"])
            QGGS_report.main(gs_basic_id, urllist["report"])
        else:
            logging.error('基本信息页访问失败！')
    else:
        logging.error('网页打开过程出错！')

       
       





