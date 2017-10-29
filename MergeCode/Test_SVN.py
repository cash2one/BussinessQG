#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : Test_SVN.py
# @Author: Lmm
# @Date  : 2017-10-13 14:56
# @Desc  :输入路径，执行svn update命令
#         首先要切换到要更新的目录，如果切换失败则，打印错误
#         然后执行更新命令
import subprocess
import os
import sys

def svn_update(path):
    with open(path+"/svn_update.txt","a+") as f:
        f.write("svn update!\n")
	try:
		os.chdir(path)
	except Exception,e:
		f.write("switch error:%s\n"%e)
		print e
		sys.exit(1)
	else:
		f.write("switch success!\n")
		
	# 获取执行输出
	mytask = subprocess.Popen('svn update --username %s --password %s' % (svnname, svnpw), shell=True,
							  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdstr = mytask.stdout.read()
	
	# 判断有没有输出错误信息
	if 'svn: E' in stdstr:
		f.write("update fail,script exit\n")
		f.write("the error message is as follows:\n")
		f.write(stdstr)
		sys.exit(1)
	else:
		f.write("svn update success!")
if __name__ == '__main__':
	#执行更新的路径
	path = ''
	# svn用户名
	svnname = ''
	#用户名
	svnpw = ''
	svn_update(path)


