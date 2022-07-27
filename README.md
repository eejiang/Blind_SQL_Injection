# Blind_SQL_Injection

# 实现布尔盲注和时间盲注的get请求方式和post请求方式

布尔盲注: 当页面没有回显位、不会输出SQL语句报错信息时，通过返回页面响应的正常或不正常的情况来进行注入

时间盲注:当页面没有回显位、不会输出SQL语句报错信息、不论SQL语句的执行结果对错都返回一样的页面时，通过页面的响应时间来进行注入


以sqli-labs为使用示例：
#python BlindBool_get.py -u http://localhost/Less-8/?id=1

#python BlindBool_post.py -u http://localhost/Less-15/

#python BlindTime_get.py -u http://localhost/Less-9/?id=1

#python BlindTime_post.py -u http://localhost/Less-15/


当您需要用此脚本探测新的页面的时候:

若您使用布尔盲注，请依据您的探测目标修改BlindBool_get.py和BlindBool_post.py中的flag变量和payload变量；

若您使用时间盲注，请依据您的探测目标修改BlindTime_get.py和BlindTime_post.py中的payload变量

