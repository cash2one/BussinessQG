#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Update_Info.py
# @Author: Lmm
# @Date  : 2017-09-28
# @Desc  : 用于对所有的分块信息进行更新

from PublicCode import config
from BranchCode import JSU_basic
from BranchCode import JSU_branch
from BranchCode import JSU_brand
from BranchCode import JSU_change
from BranchCode import JSU_check
from BranchCode import JSU_clear
from BranchCode import JSU_except
from BranchCode import JSU_freeze
from BranchCode import JSU_mort
from BranchCode import JSU_permit
from BranchCode import JSU_permit2
from BranchCode import JSU_person
from BranchCode import JSU_punish
from BranchCode import JSU_punish2
from BranchCode import JSU_report
from BranchCode import JSU_shareholder
from BranchCode import JSU_stock
from PublicCode.Public_Code import Log
import time
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# org = '8BD57D086433FE76407EBEB21C318A99'
# id = 'C7F07915079BC570367524673937ED1A'
# seq_id = '22C72034011B36A98AF38569B13712C7'
# gs_basic_id ='1900000900'
# gs_serach_id = '1'
uuid = '8BD57D086433FE76407EBEB21C318A99||C7F07915079BC570367524673937ED1A||22C72034011B36A98AF38569B13712C7'
gs_basic_id = '1900000900'
gs_search_id = '1'

# uuid = sys.argv[1]
# gs_basic_id = sys.argv[2]
# gs_search_id = sys.argv[3]
#用于获得关键的id
def get_key(uuid):
	list = uuid.split("||")
	org = list[0]
	id = list[1]
	seq_id = list[2]
	return org, id, seq_id
	

def get_all_info(org,id,seq_id,gs_basic_id,gs_search_id):
	Log().found_log(gs_basic_id,gs_search_id)
	regno = JSU_basic.main(org, id, seq_id, gs_basic_id)
	# print "regno:%s"%regno
	logging.info("regno:%s"%regno)
	JSU_branch.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_brand.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_change.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_check.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_clear.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_except.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_freeze.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_mort.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_permit.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_permit2.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_person.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_punish.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_punish2.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_shareholder.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_stock.main(org, id, seq_id, regno, gs_basic_id)
	time.sleep(config.sleep_time)
	JSU_report.main(gs_basic_id, org, id, seq_id, regno)
def main(uuid,gs_search_id,gs_basic_id):
	
	org, id, seq_id = get_key(uuid)
	get_all_info(org, id, seq_id, gs_basic_id, gs_search_id)
	
if __name__ == '__main__':
	# print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	# start = time.time()
	main(uuid, gs_search_id, gs_basic_id)
	# print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
