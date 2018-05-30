# coding=utf-8
# requirements: requests
__author__ = 'HLN'
import time
import requests
import re

HEADERS = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
}

REC_URL = ' http://xjtudj.edu.cn/course/course_updateUserWatchRecord.do'


def login():
    session = requests.session()
    # 访问主页
    # session.get("http://xjtudj.edu.cn/", headers=HEADERS)
    # 访问CAS
    response = session.get("http://xjtudj.edu.cn/pcweb/cas.jsp", headers=HEADERS)
    # 提交CAS表单
    pattern = re.compile('name="lt".*?value="(.*?)".*?name="execution".*?value="(.*?)"', re.S)
    item = re.findall(pattern, response.text)[0]
    username = input("请输入NetID:") or "hln18773372567"
    password = input("请输入密码:")
    data = {
        'username': username,
        'password': password,
        'lt': item[0],
        'execution': item[1],
        '_eventId': 'submit',
        'submit': '登录',
    }
    response = session.post(response.url, data=data, headers=HEADERS)

    # 匹配ticket（302改200了）
    pattern = re.compile('<a class="popup-with-zoom-anim.*?(http.*?)\'', re.S)
    ticket = re.findall(pattern, response.text)[0]
    # 跳转主页
    session.get(ticket, headers=HEADERS)
    HEADERS['Referer'] = ticket
    response = session.get("http://xjtudj.edu.cn/myzone/zone_index.do", headers=HEADERS)
    print("登陆成功!!!")

    # 进入进行中课程 暂只支持第一个（单）课程
    pattern = re.compile('进行中.*?newShowClassDetail\(\'(.*?)\'.*?详情', re.S)
    item = re.findall(pattern, response.text)[0]
    HEADERS['Referer'] = "http://xjtudj.edu.cn/myzone/zone_index.do"
    response = session.get("http://xjtudj.edu.cn/myzone/zone_newStudyPlanDetail.do?classID=" + item, headers=HEADERS)
    print("获取课程链接成功!!!")

    # 匹配视频列表
    HEADERS['Referer'] = "http://xjtudj.edu.cn/myzone/zone_newStudyPlanDetail.do?classID=" + item
    pattern = re.compile('已观看(&nbsp;)*([0-9]*).*?秒.*?href="(http://xjtudj.edu.cn:80/course/course_detail.do.[\w=&]*)">去观看', re.S)
    items = re.findall(pattern, response.text)
    if items:
        print("获取视频列表成功!!!")
    return session, items


def learncourse(session, nowTime, url):
    nowTime = 20
    duration = 0
    response = session.get(url).text
    pattern = re.compile('duration" value="([0-9]*)"', re.S)
    duration = int(re.findall(pattern, response)[0])

    #data
    pattern = re.compile('ccID=([0-9]*)&cateID=([0-9]*)&courseID=([0-9]*)&classID=([0-9]*)', re.S)
    item = re.findall(pattern, url)
    data = {
        'courseID': item[0][2],
        'watchTime': nowTime,
        'ccID': item[0][0],
        'classID': item[0][3]
    }
    print("已获取课程信息!!! 开始自动学习" + url + "!!!")

    while True:
        nowTime = nowTime + 40
        if nowTime > duration:
            time.sleep(0)
            data['watchTime'] = duration
            session.post(REC_URL, data=data)
            print("finish!", url)
            break
        else:
            data['watchTime'] = nowTime
            response = session.post(REC_URL, data=data)
            print(nowTime, response.status_code, url)


def main():
    courses = []
    session, courses = login()
    for course in courses:
        learncourse(session, course[1], course[2])
        print()


if __name__ == '__main__':
    main()
