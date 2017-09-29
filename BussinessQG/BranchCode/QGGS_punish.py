import hashlib
import logging
import sys
import time

from PublicCode.deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'



def name(data):
    information = {}
    for i in xrange(len(data)):
        singledata = data[i]
        number = singledata["penDecNo"]
        types = singledata["illegActType"]
        content = singledata["penContent"]
        date = singledata["penDecIssDate"]
        date = change_date_style(date)
        pub_date = singledata["publicDate"]
        pub_date = change_date_style(pub_date)
        gov_dept = singledata["penAuth_CN"]
        information[i] = [number, types, content, date, pub_date, gov_dept]
    return information


def update_to_db(gs_basic_id, cursor, connect, information):
    insert_flag = 0
    remark = 0
    try:
        for key in information.keys():
            number, types, content = information[key][0], information[key][1], information[key][2]
            date, pub_date, gov_dept = information[key][3], information[key][4], information[key][5]

            count = cursor.execute(select_punish, (gs_basic_id, number))
            if count == 0:
                m = hashlib.md5()
                m.update(str(number))
                id = m.hexdigest()

                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(punish_string, (
                gs_basic_id, id,number, types, content, date, pub_date, gov_dept, updated_time))
                insert_flag += rows_count
                connect.commit()

    except Exception, e:
        remark = 100000001
        logging.error("punish error:%s" % e)
    finally:
        if remark<100000001:
            remark = insert_flag
        return remark
