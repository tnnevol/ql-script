#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2023/2/16 10:01
# @Author  : WFRobert
# @File    : ddnsto_renewal.py
# 这是ddnsto自动续费免费7天的脚本

import os
import time
import uuid
import requests


def get_cookies():
    if os.environ.get("DDNSTO_COOKIE"):
        print("🍪已获取并使用Env环境 Cookie")
        return os.environ.get("DDNSTO_COOKIE")
    return None


def select_list(cookie):
    print('🍕开始获取csrftoken')
    # 获取令牌
    csrftoken = {}
    for line in cookie.split(';'):
        key, value = line.split('=', 1)
        csrftoken[key] = value
    csrftoken = csrftoken.get(' csrftoken')
    if csrftoken is not None:
        print_message("csrftoken获取成功")

    # 获取user_agent
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62'

    # url地址
    url = 'https://www.ddnsto.com/api/user/product/orders/'
    body = {
        "product_id": 2,
        "uuid_from_client": ''.join(uuid.uuid1().__str__().split('-'))
    }

    # 创建会话对象
    session = requests.Session()
    # 设置通用的请求头
    session.headers.update({
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'User-Agent': user_agent,
        'Cookie': cookie,
        'Content-Type': 'application/json',
        'Referer': 'https://www.ddnsto.com/app/',
        'X-CSRFToken': csrftoken,
        'Connection': 'keep-alive',
        'Host': 'www.ddnsto.com'
    })

    print('🍿开始调用接口地址')
    for i in range(3):
        print(f'😎开始第{i + 1}次调用接口，最多调用3次')
        try:
            # 关闭SSL验证
            repose = session.post(url, json=body, verify=False, timeout=5)
            text_id = repose.json()["id"]
            session.get(f"{url}/{text_id}", json=body, verify=False, timeout=5)
            session.patch("/api/user/routers/346477", json=body, verify=False, timeout=5)

            status_code = repose.status_code

            # 判断
            if 200 == status_code:
                print("😊您已成功续期")
                break
            else:
                print("😒您续期失败,这错误可能是来自于ddnsto官方的错误,因此不重复调用了,失败原因为: ", repose.text)
                break
        except Exception as e:
            print("😒您续期失败,正在尝试重新续期", e)
            time.sleep(60)
        finally:
            session.close()


# 使用函数封装重复的代码
def print_message(pr_message):
    print(f'🍪{pr_message}')


if __name__ == "__main__":
    # 使用format方法格式化字符串
    print_message('开始获取Cookie')
    cookie = get_cookies()
    print_message('获取Cookie成功')
    if cookie:
        # 使用三元表达式简化条件判断
        message = '开始调用脚本' if select_list(cookie) else '调用脚本失败'
        print_message(message)
    else:
        print_message('cookie为空，请查看您的配置文件。')