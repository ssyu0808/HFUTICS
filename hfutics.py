import json
import requests
import hashlib
import re

host = 'http://jxglstu.hfut.edu.cn'


def getCookies(username: str, password: str):
    # 拿到 salt 和 cookies
    r = requests.get(url=host + '/eams5-student/login-salt')
    cookies = requests.utils.dict_from_cookiejar(r.cookies)
    salt = r.text

    # post 请求登录
    data = {'username': username,
            # 密码是经过sha1加密
            'password': hashlib.sha1((salt + '-' + password).encode()).hexdigest(),
            'captcha': ''}
    headers = {'Host': 'jxglstu.hfut.edu.cn',
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest',
               'Content-Type': 'application/json'}
    r = requests.post(url=host + '/eams5-student/login',
                      headers=headers,
                      data=json.dumps(data),
                      cookies=cookies)
    return cookies  # dict


def getBizStuSem(cookies: dict):
    r = requests.get(url=host + '/eams5-student/for-std/course-table', cookies=cookies)
    studentId = re.findall(r'[0-9]+', re.findall('var studentId.*?;', r.text, re.M)[0])[0]
    semesterId = re.findall(r'[0-9]+', re.findall('<option selected="selected" value=".*?">', r.text, re.M)[0])[0]
    bizTypeId = re.findall(r'[0-9]+', re.findall('bizTypeId.*?,', r.text, re.M)[0])[0]
    return bizTypeId, studentId, semesterId


def getLessonIds(cookies: dict, bizTypeId: str, studentId: str, semesterId: str):
    data = {'bizTypeId': bizTypeId,
            'semesterId': semesterId,  # 学期代码
            'dataId': studentId}
    r = requests.get(url=host + '/eams5-student/for-std/course-table/get-data',
                     cookies=cookies,
                     params=data)
    lessonIDs = json.loads(r.text)['lessonIds']
    return lessonIDs  # list


def getDatum(username: str, password: str):
    cookies = getCookies(username, password)
    bizTypeId, studentId, semesterId = getBizStuSem(cookies)  # 也可以直接赋值，相关值在最后
    lessonIds = getLessonIds(cookies, bizTypeId=bizTypeId, studentId=studentId, semesterId=semesterId)
    data = {'lessonIds': lessonIds, 'studentId': studentId, 'weekIndex': ''}
    headers = {'Host': 'jxglstu.hfut.edu.cn',
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest',
               'Content-Type': 'application/json'}
    r = requests.post(url=host + '/eams5-student/ws/schedule-table/datum',
                      headers=headers,
                      data=json.dumps(data),
                      cookies=cookies)
    datum = json.loads(r.text)
    return datum  # dict


def datumToIcs(datum: dict):
    result = datum['result']
    lessonList = result['lessonList']  # 课程信息
    scheduleList = result['scheduleList']  # 每一节课
    scheduleGroupList = result['scheduleGroupList']  # 选课信息
    lessonName = {lesson['id']: lesson['courseName'] for lesson in lessonList}

    file = open('0.ics', 'w', encoding='utf8')
    file.write('''
BEGIN:VCALENDAR
PRODID:tuanzi
VERSION:2.0
X-WR-CALNAME:课表

''')
    for oneClass in scheduleList:
        DTSTART = 'DTSTART:{}T{:0>4d}00Z'.format(oneClass['date'].replace('-', ''), oneClass['startTime'] - 800)
        DTEND = 'DTEND:{}T{:0>4d}00Z'.format(oneClass['date'].replace('-', ''), oneClass['endTime'] - 800)
        DESCRIPTION = 'DESCRIPTION:' + oneClass['personName']
        if oneClass['room'] != None:
            LOCATION = 'LOCATION:' + oneClass['room']['nameZh']
        else:
            LOCATION = 'LOCATION:未安排教室'
        SUMMARY = 'SUMMARY:' + lessonName[oneClass['lessonId']]
        file.write('BEGIN:VEVENT' + '\n')
        file.write('UID:'
                   + hashlib.sha1(lessonName[oneClass['lessonId']].encode(encoding='utf-8')).hexdigest()
                   + '-{}T{:0>4d}00Z'.format(oneClass['date'].replace('-', ''), oneClass['startTime'] - 800)
                   + '-{}T{:0>4d}00Z'.format(oneClass['date'].replace('-', ''), oneClass['endTime'] - 800)
                   + '\n')
        file.write('DTSTAMP:20190101T000000Z' + '\n')
        file.write(DTSTART + '\n')
        file.write(DTEND + '\n')
        file.write(DESCRIPTION + '\n')
        file.write(LOCATION + '\n')
        file.write(SUMMARY)
        file.write('''
BEGIN:VALARM
TRIGGER:-PT10M
REPEAT:2
DURATION:PT5M
ACTION:DISPLAY
DESCRIPTION:设置了也不会显示
END:VALARM
''')
        file.write('END:VEVENT' + '\n')
        file.write('\n')
    file.write('END:VCALENDAR' + '\n')

    file.close()


def getTimeTableIcs(username: str, password: str):
    datumToIcs(getDatum(username, password))


# 1. username = 'xxxxxxxxxx'  学号
# 2. password = 'xxxxxx'      身份证后六位
# 3. 默认是生成本学期的，可以修改第64行左右 semesterId = 来生成其它学期的
# 4. 程序不进行任何异常捕获，所以不保证运行正常
# 5. 2020/06/08 测试正常
# 6. 适用于新版教务系统
# 7. 运行环境: python37 需要的包: json requests re hashlib(python3自带)
# 8. 作者: tuanzi

print('说明:')
print('-有关密码')
print('\t- 合肥校区初始密码是身份证后六位(x小写)')
print('\t- 宣城校区初始密码是学号')
print('\t- 修改过密码可以在 [信息门户->本科教务->你好，XXX(右上角)->账号设置] 查看')
print('-有关ics文件')
print('\t- 生成的ics文件符合RFC 5545标准, 遵循这个协议的邮箱/日历类软件理论上都可以使用')
print('\t- 推荐使用outlook日历网页端进行导入 ( https://outlook.live.com/calendar )')
print('-有关项目')
print('\t- 作者: tuanzi')
print('\t- 项目源码地址 https://github.com/ssyu0808/HFUTICS')
print('\n')
username = input('输入学号: ')
password = input('输入密码: ')

getTimeTableIcs(username=username, password=password)

print('我也不知道成没成，看一下当前目录下的0.ics文件有没有内容吧！')
input('按任意键退出...')

