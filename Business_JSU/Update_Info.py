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

org = '78AB4DDC058110BDAA3B82E7C2990A07'
id = '4D6557472C5E5A088C887D721414358B'
seq_id = 'C486462EC151CB99F84896EC5D0A4AD4'
gs_basic_id ='1900000902'
gs_py_id = '1'

# org = sys.argv[1]
# id = sys.argv[2]
# seq_id = sys.argv[3]
# gs_basic_id = sys.argv[4]
# gs_py_id = sys.argv[5]


def get_all_info(org,id,seq_id,gs_basic_id,gs_py_id):
	Log().found_log(gs_py_id,gs_basic_id)
	regno = JSU_basic.main(org, id, seq_id, gs_basic_id, gs_py_id)
	logging.info("regno:%s"%regno)
	# JSU_branch.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	JSU_person.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	time.sleep(config.sleep_time)
	# JSU_shareholder.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_change.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_report.main(gs_basic_id, org, id, seq_id, regno, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_brand.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	
	# JSU_check.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_clear.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_except.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_freeze.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_mort.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_permit.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_permit2.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	
	# JSU_punish.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	# JSU_punish2.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	#
	# JSU_stock.main(org, id, seq_id, regno, gs_basic_id, gs_py_id)
	# time.sleep(config.sleep_time)
	
	
	
if __name__ == '__main__':
	# print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	# start = time.time()
	get_all_info(org, id, seq_id, gs_basic_id,gs_py_id)
	# print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
