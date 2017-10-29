#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Judge_Status.py
# @Author: Lmm
# @Date  : 2017-07-28
# @Desc  : 用于判断更新过程中的状态

import sys
import time
from Public_code import Get_BranchInfo
import config

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
class Judge:
    def __init__(self,gs_basic_id,url):
        self.gs_basic_id = gs_basic_id
        self.url = url
    def judge_status(self,recodestotal,total):
        if recodestotal == 0:
            flag = -1
        elif recodestotal == -1:
            flag = 100000004
        elif recodestotal > 0 and total >= 0 and total < 100000001:
            flag = total
        elif recodestotal >-1 and total > 100000001:
            flag = 100000006
        return flag
    
    def update_branch(self,QGGS,name):
        
        recordstotal, total, insert_total, update_total=Get_BranchInfo().get_info(None, self.gs_basic_id, self.url,QGGS, name)
        flag = self.judge_status(recordstotal,total)
        print "%s:"%name +str(flag)+str(recordstotal)+str(update_total)+str(insert_total)