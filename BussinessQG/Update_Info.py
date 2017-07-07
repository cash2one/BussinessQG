#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author liangmengmeng

# from GetUrl import *
# from Main_get_info import *

# from QGGS_Report import *

import logging
import sys
import time

from BranchCode.GetUrl import *
from Main_get_info import *
from PublicCode import coutnumber
from PublicCode.Public_code import Connect_to_DB

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# 配置日志文件start-----------------------------------------------------------------
# gs_basic_id = sys.argv[1]
# code = sys.argv[2]
#110000017421980 229417850
gs_basic_id = 229417758
code = '91310000132206289R'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='./log/%s_main_%s.log' % (time.strftime("%Y-%m-%d ", time.localtime()), code),
                    filemode='w')


# 配置日志文件End-------------------------------------------------------------------
def main():
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        challenge, validate, cookies = loop_break_password()
        information = last_request(challenge, validate, code, cookies)
        if len(information) > 0:
            url = information[code][0]
            print url
            # update_db(information, cursor, connect)
            update_info_main(cursor, connect, url, gs_basic_id)
        connect.close()
    except Exception, e:
        logging.info("main error: %s" % e)
    finally:
        print coutnumber.counthtml
        print coutnumber.countexcute


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
