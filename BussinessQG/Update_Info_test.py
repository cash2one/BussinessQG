#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author liangmengmeng

from BranchCode.GetUrl import *
from PublicCode.Public_code import Connect_to_DB
from Main_get_info import *
import sys
import time
import logging

# from QGGS_Report import *cc
reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()



select_code = 'select gs_basic_id,code from gs_basic limit 100'


def main():
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        cursor.execute(select_code)
        for gs_basic_id, code in cursor.fetchall():
            print code, gs_basic_id
            challenge, validate, cookies = loop_break_password()
            information = last_request(challenge, validate, code, cookies)
            if len(information) != 0:
                update_db(information, cursor, connect)
                update_info_main(cursor, connect, code)
        connect.close()
    except Exception, e:
        print e
        logging.info("main error: %s" % e)


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
