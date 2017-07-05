import logging
import sys
import time
import hashlib

from deal_html_code import change_date_style

reload(sys)
sys.setdefaultencoding('utf-8')
Type = sys.getfilesystemencoding()
punish_string = 'insert into gs_punish(gs_basic_id,id,number, types, content,date, pub_date, gov_dept,updated)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
select_punish = 'select gs_punish_id from gs_punish where gs_basic_id = %s and number = %s'
update_punish = 'update gs_punish set types = %s ,content = %s,date = %s,pub_date = %s,gov_dept = %s ,updated = %s where gs_punish_id = %s'


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
    insert_flag, update_flag = 0, 0
    for key in information.keys():
        number, types, content = information[key][0], information[key][1], information[key][2]
        date, pub_date, gov_dept = information[key][3], information[key][4], information[key][5]
        try:
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
            elif count == 1:
                gs_punish_id = cursor.fetchall()[0][0]
                updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                rows_count = cursor.execute(update_punish,
                                            (types, content, date, pub_date, gov_dept, updated_time, gs_punish_id))
                update_flag += rows_count
                connect.commit()
        except Exception, e:
            # print "punish error:", e
            logging.error("punish error:%s" % e)
    flag = insert_flag + update_flag
    # print insert_flag, update_flag
    # print flag
    return flag
