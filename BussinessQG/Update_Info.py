#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @author liangmengmeng


import logging
from BranchCode.GetUrl import *
from Main_get_info import *
from PublicCode.Public_code import Connect_to_DB
from PublicCode import config

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
# 配置日志文件start-----------------------------------------------------------------
# gs_basic_id = sys.argv[1]
# code = sys.argv[2]
#gs_py_id = sys.argv[3]
#110000017421980 229417850
user_id = 1369
gs_basic_id = 229418488
code = '914100001699995779'
ccode = ''

log_path = config.log_path
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=log_path+'/log/%s_main_%s_%s.log' % (time.strftime("%Y-%m-%d ", time.localtime()), gs_basic_id,user_id),
                    filemode='w')


# 配置日志文件End-------------------------------------------------------------------
insert_basic_py = 'insert into gs_py(user_id,gs_basic_id,updated)values(%s,%s,%s)'
update_basic_py = 'update gs_py set gs_py_id = %s,gs_basic = %s,updated = %s where gs_py_id = %s and gs_basic_id = %s'

def main():
    try:
        HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
        connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
        challenge, validate, cookies = loop_break_password()
        url, flag = last_request(challenge, validate, code, ccode, cookies)
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        cursor.execute(insert_basic_py, (user_id,gs_basic_id,updated_time))
        gs_py_id = connect.insert_id()
        if url!= None:
            update_info_main(cursor, connect, url, flag, gs_basic_id, gs_py_id)
        else:
            cursor.execute(update_basic_py, ( gs_py_id, flag, updated_time, gs_py_id,gs_basic_id))
            connect.commit()
    except Exception, e:
        logging.info("main error: %s" % e)
    finally:
        cursor.close
        connect.close()


if __name__ == "__main__":
    print "The Program start time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    start = time.time()
    main()
    print "The Program end time:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "[%s]" % (time.time() - start)
