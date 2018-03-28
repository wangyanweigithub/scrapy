#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import base64

from tengxunhouse.settings import USER_AGENTS
from tengxunhouse.settings import PROXIES

# 随机的User-Agent
class RandomUserAgent(object):
    def process_request(self, request, spider):
        useragent = random.choice(USER_AGENTS)
        #print useragent
        request.headers.setdefault("User-Agent", useragent)

class RandomProxy(object):
    def process_request(self, request, spider):
        # proxy = random.choice(PROXIES)
        proxy = random.choice(PROXIES)

        print("proxy:",proxy)


        if proxy['user_passwd'] == '':        #proxy['user_passwd'] is None:
            # 没有代理账户验证的代理使用方式
            # print("null")
            request.meta['proxy'] = "http://" + proxy['ip_port']

        else:
            print("test",len(proxy['user_passwd']))
            # 对账户密码进行base64编码转换
            print("proxy['user_passwd']:",proxy['user_passwd'])
            base64_userpasswd = base64.b64encode(proxy['user_passwd'].decode())
            # 对应到代理服务器的信令格式里
            request.headers['Proxy-Authorization'] = 'Basic ' + base64_userpasswd

            request.meta['proxy'] = "http://" + proxy['ip_port']