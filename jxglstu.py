import re

import requests
import hashlib


class hfut():
    """合肥工业大学 教务系统"""
    # 教务系统地址
    host = 'http://jxglstu.hfut.edu.cn'
    username = ''
    password = ''
    #
    studentId = ''
    semesterId = ''
    bizTypeId = ''
    #
    r = requests.session()

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        salt = self.r.get('{host}/eams5-student/login-salt'.format(host=self.host)).text
        data = {'username': self.username,
                'password': hashlib.sha1((salt + '-' + self.password).encode('utf-8')).hexdigest(),
                'captcha': ''}
        self.r.post(url='{host}/eams5-student/login'.format(host=self.host), json=data)
        return self

    def set(self):
        result = self.r.get('{host}/eams5-student/for-std/course-table'.format(host=self.host))
        self.studentId = re.search(r'(?<=var studentId = )\d+', result.text)[0]
        self.semesterId = re.search(r'(?<=<option selected="selected" value=")\d+', result.text)[0]
        self.bizTypeId = re.search(r'(?<=bizTypeId: )\d+', result.text)[0]
        return self

    def getDatum(self):
        params = {'bizTypeId': self.bizTypeId,
                  'semesterId': self.semesterId,  # 学期代码
                  'dataId': self.studentId}
        lessonIds = self.r.get(url='{host}/eams5-student/for-std/course-table/get-data'.format(host=self.host),
                               params=params).json()['lessonIds']
        data = {'lessonIds': lessonIds, 'studentId': self.studentId, 'weekIndex': ''}
        datum = self.r.post(url='{host}/eams5-student/ws/schedule-table/datum'.format(host=self.host),
                            json=data).json()
        return datum


hfut('2017211220', '081272').login().set().getDatum()
