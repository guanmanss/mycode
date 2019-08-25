# -*- coding:utf-8 -*-
import urllib.request
import urllib
import socket
import threading
import pandas as pd
from lxml import etree
import random
import json

class Duo_dazhong(object):

    def __init__(self):
        # 整理代理IP格式
        self.proxys = []
        self.inFile = open('proxy_ip2.txt', 'r')
        self.name_file = pd.read_excel("name_file.xlsx")
        self.num_list = self.name_file.iloc[:,1].values
        self.start_urls = [f"http://www.dianping.com/shop/{int(i)}" for i in self.num_list[128195:150000]]
        # proxy_ip = open('proxy_ip1.txt', 'a')  # 新建一个储存有效IP的文档
        for line in self.inFile.readlines():
            lines = line.replace("\n","")
            # proxy_host = lines
            self.proxys.append(lines)
        self.lock = threading.Lock()  # 建立一个锁
    # 代理IP发起请求
    def reqe(self,url,a):
        global foo
        foo = False
        socket.setdefaulttimeout(3)  # 设置全局超时时间
        url = url  # 打算爬取的网址
        try:
            po = {"http": self.proxys[a]}
            proxy_support = urllib.request.ProxyHandler(po)
            opener = urllib.request.build_opener(proxy_support)
            opener.addheaders = [("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36")]
            urllib.request.install_opener(opener)
            # time.sleep(random.randint(2, 4))
            res = urllib.request.urlopen(url).read()
            html = etree.HTML(res.decode())
            items = html.xpath('//div[@id="basic-info"]')
            if len(items) == 0:
                foo = False
                print(self.proxys[a], "跳转验证中心")
                return '0'
            else:
                self.lock.acquire()
                foo = True
                # print(self.proxys[a], "ok")
                self.lock.release()
                return items
        except Exception as e:
            self.lock.acquire()
            print(self.proxys[a], e)
            foo = False
            self.lock.release()

    def reqe2(self,res,a):
        try:
            dic = {}
            if res == '0':
                dic['ip'] = str(a).split('/')[-1]
            else:
                dic['ip'] = str(a).split('/')[-1]
                for item in res:
                    name = item.xpath('./h1/text()')[0]
                    dic['name'] = name.strip()
            print(dic)
            # 获取锁，用于线程同步
            self.lock.acquire()  # 获得锁
            self.save_data(dic)
            # proxy_ip.write('%s\n' % str(proxys[i]))  # 写入该代理IP
            # 释放锁，开启下一个线程
            self.lock.release()  # 释放锁
        except Exception as e:
            self.lock.acquire()
            self.lock.release()

    def save_data(self,datas):
        items = json.dumps(datas, ensure_ascii=False)
        with open("dazhong2.json", 'a', encoding="utf8")as f:
            f.write(items + ',\n')

    def run(self):
        threads = []
        # start = time.clock()
        a = random.randint(0, len(self.proxys) - 1)
        j = 0
        for i in self.start_urls:
            while True:
                ass = self.reqe(i, a)
                if ass == '0':
                    j += 1
                if foo == True:
                    thread = threading.Thread(target=self.reqe2, args=[ass, i])
                    threads.append(thread)
                    thread.start()
                    j = 0
                    break
                else:
                    a1 = random.randint(0, len(self.proxys) - 1)
                    a = a1
                    if j > 3:
                        thread = threading.Thread(target=self.reqe2, args=[ass, i])
                        threads.append(thread)
                        thread.start()
                        j = 0
                        break
        for thread in threads:
            thread.join()
        # proxy_ip.close()  # 关闭文件
        # end = time.clock()

if __name__ == '__main__':
    duo = Duo_dazhong()
    duo.run()