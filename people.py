# coding=utf-8
# requirements: requests
__author__ = 'HLN'
import time
import requests
import re
import csv

HEADERS = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36',
}

username = ""
password = ""


def login():
    session = requests.session()
    # 访问主页
    # session.get("http://xjtudj.edu.cn/", headers=HEADERS)
    # 访问CAS
    response = session.get("http://xjtudj.edu.cn/pcweb/cas.jsp", headers=HEADERS)
    # 提交CAS表单
    pattern = re.compile('name="lt".*?value="(.*?)".*?name="execution".*?value="(.*?)"', re.S)
    item = re.findall(pattern, response.text)[0]
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
    if response.status_code == 200:
        print("登陆成功!!!")
        return session
    else:
        print("登陆失败!!!")
        time.sleep(5)
        session = login()
        return session


def save(people):
    with open('./people.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), people])
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "," + people)


def sleep():
    sleeptime = {
        '0': 10,
        '1': 10,
        '2': 30,
        '3': 30,
        '4': 30,
        '5': 30,
        '6': 30,
        '7': 10,
        '8': 10,
        '9': 10,
        '10': 30,
        '11': 30,
        '12': 5,
        '13': 5,
        '14': 5,
        '15': 30,
        '16': 30,
        '17': 30,
        '18': 5,
        '19': 5,
        '20': 5,
        '21': 5,
        '22': 5,
        '23': 5,
    }
    time.sleep(sleeptime[str(time.localtime().tm_hour)])


def main():
    global username
    global password
    username = input("请输入NetID:") or "hln18773372567"
    password = input("请输入密码:")
    session = login()
    while True:
        response = session.get("http://xjtudj.edu.cn/myzone/zone_index.do", headers=HEADERS)
        pattern = re.compile('在线人数[\D]*([\d]*)人', re.S)
        people = re.findall(pattern, response.text)
        if people:
            save(people[0])
        else:
            save(-1)
            time.sleep(5)
            session = login()
        sleep()


if __name__ == '__main__':
    main()
