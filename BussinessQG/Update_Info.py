#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author liangmengmeng
import logging
import sys

from GetUrl import *
from Main_get_info import *

# from QGGS_Report import *
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# 配置日志文件start-----------------------------------------------------------------

code = '914305007073048253'
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='%s_main_%s.log' % (time.strftime("%Y-%m-%d ", time.localtime()), code),
                    filemode='w')


# 配置日志文件End-------------------------------------------------------------------
def main():
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        challenge, validate, cookies = loop_break_password()
        information = last_request(challenge, validate, code, cookies)
        update_db(information, cursor, connect)
        update_info_main(cursor, connect, code)
        connect.close()
    except Exception, e:
        logging.info("main error: %s" % e)


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
