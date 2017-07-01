#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
import time

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()


def deal_lable(html_code):
    pattern = re.compile('<.*?>.*?</.*?>', re.S)
    result = re.sub(pattern, '', html_code)
    return result


def change_date_style(old_date):
    if old_date == '' or old_date == None:
        new_date = None
    else:
        new_date = time.localtime(old_date / 1000)
        otherStyleTime = time.strftime('%Y-%m-%d ', new_date)
        new_date = otherStyleTime
    return new_date
