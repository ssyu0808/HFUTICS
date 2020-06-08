import json
import requests
import hashlib
import re


host = 'http://jxglstu.hfut.edu.cn'


def getCookies(username: str, password: str):
    # 拿到 salt 和 cookies
    r = requests.get(url=host+'/eams5-student/login-salt')
    cookies = requests.utils.dict_from_cookiejar(r.cookies)
    salt = r.text

    # post 请求登录
    data = {'username': username,
            # 密码是经过sha1加密
            'password': hashlib.sha1((salt+'-'+password).encode()).hexdigest(),
            'captcha': ''}
    headers = {'Host': 'jxglstu.hfut.edu.cn',
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest',
               'Content-Type': 'application/json'}
    r = requests.post(url=host+'/eams5-student/login',
                      headers=headers,
                      data=json.dumps(data),
                      cookies=cookies)
    return cookies  # dict


def getStudentId(cookies: dict):
    r = requests.get(url=host+'/eams5-student/for-std/course-table',
                     cookies=cookies)
    studentId = re.findall(
        r'[0-9]+', re.findall('var studentId.*?;', r.text, re.M)[0])[0]
    return studentId  # str


def getSemesterId(cookies: dict):
    r = requests.get(url=host+'/eams5-student/for-std/course-table',
                     cookies=cookies)
    semesterId = re.findall(
        r'[0-9]+', re.findall('<option selected="selected" value=".*?">', r.text, re.M)[0])[0]
    return semesterId  # str


def getLessonIds(cookies: dict, studentId: str, semesterId: str):
    data = {'bizTypeId': '2',         # 还没搞懂这个参数什么意思
            'semesterId': semesterId,  # 学期代码
            'dataId': studentId}
    r = requests.get(url=host+'/eams5-student/for-std/course-table/get-data',
                     cookies=cookies,
                     params=data)
    lessonIDs = json.loads(r.text)['lessonIds']
    return lessonIDs  # list


def getDatum(username: str, password: str):
    cookies = getCookies(username, password)
    studentId = getStudentId(cookies)
    semesterId = getSemesterId(cookies)  # 也可以直接赋值，相关值在最后
    lessonIds = getLessonIds(cookies, studentId, semesterId=semesterId)
    data = {'lessonIds': lessonIds,
            'studentId': studentId,
            'weekIndex': ''}
    headers = {'Host': 'jxglstu.hfut.edu.cn',
               'Connection': 'keep-alive',
               'X-Requested-With': 'XMLHttpRequest',
               'Content-Type': 'application/json'}
    r = requests.post(url=host+'/eams5-student/ws/schedule-table/datum',
                      headers=headers,
                      data=json.dumps(data),
                      cookies=cookies)
    datum = json.loads(r.text)
    return datum  # dict


def datumToIcs(datum: dict):
    result = datum['result']
    lessonList = result['lessonList']                # 课程信息
    scheduleList = result['scheduleList']            # 每一节课
    scheduleGroupList = result['scheduleGroupList']  # 选课信息
    lessonName = {lesson['id']: lesson['courseName'] for lesson in lessonList}

    file = open('0.ics', 'w', encoding='utf8')
    file.write('''
BEGIN:VCALENDAR
PRODID:tuanzi
VERSION:2.0
X-WR-CALNAME:课表

BEGIN:VTIMEZONE
TZID:China Standard Time
BEGIN:STANDARD
DTSTART:16010101T000000
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
END:STANDARD
BEGIN:DAYLIGHT
DTSTART:16010101T000000
TZOFFSETFROM:+0800
TZOFFSETTO:+0800
END:DAYLIGHT
END:VTIMEZONE

''')

    for oneClass in scheduleList:
        DTSTART = 'DTSTART;TZID=China Standard Time:{date}T{startTime:0>4d}00'.format(
            date=oneClass['date'].replace('-', ''), startTime=oneClass['startTime'])
        DTEND = 'DTEND;TZID=China Standard Time:{date}T{endTime:0>4d}00'.format(
            date=oneClass['date'].replace('-', ''), endTime=oneClass['endTime'])
        DESCRIPTION = 'DESCRIPTION:'+oneClass['personName']
        LOCATION = 'LOCATION:'+oneClass['room']['nameZh']
        SUMMARY = 'SUMMARY:'+lessonName[oneClass['lessonId']]
        file.write('BEGIN:VEVENT'+'\n')
        file.write(DTSTART+'\n')
        file.write(DTEND+'\n')
        file.write(DESCRIPTION+'\n')
        file.write(LOCATION+'\n')
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
        file.write('END:VEVENT'+'\n')
        file.write('\n')
    file.write('END:VCALENDAR'+'\n')

    file.close()


def getTimeTableIcs(username: str, password: str):
    datumToIcs(getDatum(username, password))


# 1. username = 'xxxxxxxxxx'  学号
# 2. password = 'xxxxxx'      身份证后六位
# 3. 默认是生成本学期的，可以修改第64行左右 semesterId = 来生成其它学期的
# 4. 程序不进行任何异常捕获，所以不保证运行正常
# 5. 2020/06/08 测试正常
# 6. 适用于新版教务系统（宣区请勿尝试）
# 7. 运行环境: python37 需要的包: json requests re hashlib(python3自带)
# 5. 作者: tuanzi

username = input('输入学号：')
password = input('输入密码（身份证后六位）：')


getTimeTableIcs(username=username, password=password)

print('我也不知道成没成，看一下当前目录下的0.ics文件有没有内容吧！')
input('按任意键退出···')

# 114 2020-2021学年第一学期
# 94  2019-2020学年第二学期
# 74  2019-2020学年第一学期
# 54  2018-2019学年第二学期
# 35  2018-2019学年第一学期
# 33  2017-2018学年第二学期
# 32  2017-2018学年第一学期
# 31  2016-2017学年第二学期
# 30  2016-2017学年第一学期
# 29  2015-2016学年第二学期
# 28  2015-2016学年第一学期
# 27  2014-2015学年第二学期
# 26  2014-2015学年第一学期
# 25  2013-2014学年第二学期
