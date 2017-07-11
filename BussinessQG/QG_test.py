#!/usr/bin/env python
# -*- coding:utf-8 -*-


from PublicCode import config
from PublicCode.Public_code import Connect_to_DB
HOST, USER, PASSWD, DB, PORT = config.HOST, config.USER, config.PASSWD, config.DB, config.PORT
connect, cursor = Connect_to_DB().ConnectDB(HOST, USER, PASSWD, DB, PORT)
gs_basic_id = 229418487
# select_person = 'select  updated from gs_person where gs_basic_id = %s order by updated desc  LIMIT 1'
# flag = cursor.execute(select_person, gs_basic_id)
string = '2017-07-07 09:43:00'
select_person = 'select updated from gs_person where gs_basic_id = %s and updated > %s '
flag = cursor.execute(select_person, (gs_basic_id,string))
print type(cursor.fetchall()[0][0])
print type(string)