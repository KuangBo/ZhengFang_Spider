# coding=utf-8
import requests
import urllib
import re
import os
from lxml import etree
from bs4 import BeautifulSoup
from ZhengFang_System_Spider import predict
# from ZhengFang_System_Spider import check_img, check_predict


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.urlname = ''


class ZFSpider:
    def __init__(self, student):
        self.baseUrl = "http://210.44.14.34"
        self.student = student
        self.session = requests.session()
        self.session.headers['User-Agent'] =\
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'
        # 定义登陆字典
        self.postData_land = {'__VIEWSTATE': '',
                              'TextBox1': '',
                              'TextBox2': '',
                              'TextBox3': '',
                              'RadioButtonList1': '',
                              'Button1': '',
                              'hidPdrs': '',
                              'hidsc': ''}
        # 定义获取成绩字典
        self.postData_getGrade = {'Button2': '',
                                  'txtZZCJ': '',
                                  'txtQSCJ': '',
                                  'ddlXQ': '',
                                  'ddlXN': '',
                                  '__VIEWSTATE': '',
                                  '__EVENTTARGET': '',
                                  '__EVENTARGUMENT': ''}

    def login(self):
        # 拼凑登陆界面的url
        url = self.baseUrl + '/default5.aspx'
        res = self.session.get(url)
        # 使用lxml中的etree解析HTML文件
        selector = etree.HTML(res.content)
        # 将获取到的__VIEWSTATE值添加到字典
        self.postData_land['__VIEWSTATE'] = selector.xpath('//*[@id="form1"]/input/@value')[0]
        # 拼凑验证码界面的url
        img_url = self.baseUrl + '/CheckCode.aspx'
        # 获取验证码
        img_res = self.session.get(img_url)
        with open('./cache/check.png', 'wb') as f:
            f.write(img_res.content)
        # image = Image.open('./cache/check.png')
        # image.show()
        # 处理验证码并放到字典
        # check_img.process()
        self.postData_land['TextBox3'] = predict.handle_image('./cache/check.png')
        print("CheckCode:" + self.postData_land['TextBox3'])
        # 将其他信息放入字典
        self.postData_land['TextBox1'] = self.student.username
        self.postData_land['TextBox2'] = self.student.password
        self.postData_land['RadioButtonList1'] = urllib.parse.quote_plus(u"学生".encode('gbk'))
        # 发送登陆请求
        login_res = self.session.post(url, data=self.postData_land)
        # 寻找路径学号是否匹配来验证是否登陆成功
        pattern = re.compile('<form name="Form1" method="post" action="(.*?)" id="Form1">')
        res = re.findall(pattern, login_res.content.decode('gbk'))
        try:
            if res[0][16:] == self.student.username:
                print("登陆成功！")
        except:
            print("登陆失败！")
            return False
        # 登陆成功，找到学生姓名存在User中
        pattern = re.compile('<span id="xhxm">(.*?)同学</span>')
        xhxm = re.findall(pattern, login_res.content.decode('gbk'))
        self.student.urlname = urllib.parse.quote_plus(xhxm[0].encode('gbk'))
        return True

    def get_grade(self):
        # 设置session头信息
        self.session.headers['Referer'] = self.baseUrl + '/xs_main.aspx?xh=' + self.student.username
        # 拼凑获取成绩的url
        grade_url = self.baseUrl + '/xscj.aspx?xh=' + self.student.username + '&xm=' + self.student.urlname + '&gnmkdm=N121604'
        grade_res = self.session.get(grade_url)
        soup = BeautifulSoup(grade_res.content.decode('gbk'), 'lxml')
        # 将数据放入字典postData_getGrade中
        self.postData_getGrade['__VIEWSTATE'] = soup.find('input', attrs={'name': '__VIEWSTATE'})['value']
        self.postData_getGrade['txtQSCJ'] = 0
        self.postData_getGrade['txtZZCJ'] = 100
        self.postData_getGrade['Button2'] = urllib.parse.quote_plus(u'在校学习成绩查询'.encode('gbk'))
        gra_res = self.session.post(grade_url, data=self.postData_getGrade)
        grades = GetGrade(gra_res)
        totup = 0
        totdown = 0
        f = open(os.getcwd() + '/Grade_Point.txt', 'a+', encoding='utf-8')
        f.write('\n\n\n' + u'历年成绩:' + '\n')
        for i in grades[0]:
            f.write('%-13s\t' % i)
        f.write('\n')
        for each in grades:
            if each[u'课程性质'] != '任选':
                for one in each:
                    f.write('%-15s\t' % each[one])
                f.write('\n')
                totup = totup + GetPoint(each) * float(each[u'学分'])
                totdown = totdown + float(each[u'学分'])
        f.write('\n' + u'平均绩点: ' + '%.2f\t\t\t' % (
                totup / totdown) + u'总学分绩点: ' + '%.2f\t\t\t' % totup + u'总学分: ' + '%.2f\n' % totdown)
        f.close()
        print('Download grade succeed!')


def GetGrade(response):
    soup = BeautifulSoup(response.content.decode('gbk'), 'lxml')
    trs = soup.find(id="DataGrid1").findAll("tr")
    Grades = []
    keys = []
    tds = trs[0].findAll("td")
    # tds = tds[:5] + tds[6:9]
    for td in tds:
        keys.append(td.string)
    for tr in trs[1:]:
        tds = tr.findAll("td")
        # tds = tds[:5] + tds[6:9]
        values = []
        for td in tds:
            values.append(td.string)
        one = dict((key, value) for key, value in zip(keys, values))
        Grades.append(one)
    return Grades


def GetPoint(each):
    if each[u'课程性质'] != '任选':
        if each[u'成绩'] == '良好':
            point = 3.5
        else:
            grade = float(each[u'成绩'])
            point = (grade - 50) / 10
        return point


user_name = input(u'UserName:')
pass_word = input(u'PassWord:')
stu = User(user_name, pass_word)
ZF = ZFSpider(stu)
for i in range(1, 5):
    flag = False
    if ZF.login():
        ZF.get_grade()
        break
