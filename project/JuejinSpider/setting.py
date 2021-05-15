# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目配置信息模块 }
# @Date: 2021/05/10 12:11
import utils
import random

# 作者信息
AUTHOR = '作者名'
ACCOUNT = '掘金登录账号'
PASSWORD = '登录密码'

# 注意浏览器驱动要跟本地浏览器版本对应
# 谷歌浏览器驱动路径
CHROME_WEB_DRIVER = r'./driver/chromedriver.exe'

# Edge浏览器驱动
EDGE_WEB_DRIVER = r''

# 火狐浏览器驱动
FIREFOX_WEB_DRIVER = r''

# 存储已经评论过的文章数据json文件
COMMENTED_JSON = r'./data/commented.json'

# 存储用户登录后的Cookies数据的json文件
COOKIES_JSON = r'./data/user_cookies.json'

# 存储掘金所有标签的json文件
TAG_JSON = r'./data/tag.json'

# 浏览器驱动隐式等待时间
IMPLICIT_WAIT_TIME = 10

# 如果启用无界面模式，需要设置屏幕分辨率
# 动态获取系统屏幕分辨率
SCREEN_X, SCREEN_Y = utils.get_real_screen()


class ArticleCategory:
    """掘金文章默认分类"""
    recommended = '推荐'
    following = '关注'
    BACKEND = '后端'
    FRONTEND = '前端'
    ANDROID = 'android'
    IOS = 'ios'
    AI = '人工智能'
    FREEBIE = '开发工具'
    CAREER = '代码人生'
    ARTICLE = '阅读'
    DEFAULT = BACKEND


class LoginMode:
    """登录模式类"""
    ACCOUNT = 1
    COOKIES = 2
    REQUEST = 3
    DEFAULT = ACCOUNT


class ArticleSort:
    """文章排序规则类"""
    COMPREHENSIVE = '综合'
    NEWEST = '最新'
    HOTTEST = '最热'

    # 在这里更改你所需要的文章排序规则
    DEFAULT = NEWEST


# 评论文章数量
COMMENT_ARTICLE_NUMS = 2

# 评论间隔 [1, 3) 分钟
# COMMENT_INTERVAL = (60, 3 * 60)

# 测试 [3, 5) 秒
COMMENT_INTERVAL = (3, 5)

# 评论结尾语
COMMENT_END_MESSAGES = [
    '欢迎回访',
    '期待回访',
    '可以来康康我的吗'
]

# 通用评论
GENERAL_COMMENTS = [
    '写的不错，给你竖大拇指，' + random.choice(COMMENT_END_MESSAGES),
    '博主的文章着实不错，给你点赞， ' + random.choice(COMMENT_END_MESSAGES),
    '到此一游',
    '值得学习，' + random.choice(COMMENT_END_MESSAGES),
    '文采四溢，赞一波，' + random.choice(COMMENT_END_MESSAGES),
    '学到了，收藏一波~',
    '来大佬博客串串门，学习学习',
    '受益匪浅',
    '创作不易，给你点赞，继续创作优质好文！',
    '代码之路任重道远，愿跟博主努力学习之',
    '干货满满，很详细，评论占个坑。欢迎一起交流'
]

# User-Agent 的请求头信息
UA_LIST = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
    "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
]


def main():
    print(SCREEN_X, SCREEN_Y)


if __name__ == '__main__':
    main()
