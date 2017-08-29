#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Patent_basic.py
# @Author: Lmm
# @Date  : 2017-08-29
# @Desc  :
class Ia_Patent:
    #用于获取基本信息
    def get_info(self,url):
        cookies["IS_LOGIN"] = 'true'
        user_agent = random.choice(config.USER_AGENTS)
        headers["User-Agent"] = user_agent

    #用于将基本信息更新到数据库中
    def update_to_db(self,info,cursor,connect):
