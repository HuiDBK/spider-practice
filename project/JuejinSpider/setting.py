# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 项目配置信息模块 }
# @Date: 2021/05/10 12:11
import utils
import random

# 作者信息
AUTHOR = '输入你的作者名称'
ACCOUNT = '输入你的账号'
PASSWORD = '输入你的密码'

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

# 浏览器驱动隐式等待时间
IMPLICIT_WAIT_TIME = 10

# 如果启用无界面模式，需要设置屏幕分辨率
# 动态获取系统屏幕分辨率
SCREEN_X, SCREEN_Y = utils.get_real_screen()

# 目前只支持后端部分分类文章自动评论
# 后期可改成动态获取
BACKEND_CATEGORY = {
    'python': '/backend/Python',
    'java': '/backend/Java',
    '后端': '/backend/后端',
    'go': '/backend/Python',
    'mysql': '/backend/MySQL',
    'spring': '/backend/Spring',
    '数据库': '/backend/数据库',
    'jvm': '/backend/JVM',
    'linux': '/backend/Linux',
}


class LoginMode:
    """登录模式类"""
    ACCOUNT = 1
    COOKIES = 2
    DEFAULT = ACCOUNT


# 评论结尾语
COMMENT_END_MESSAGES = [
    '欢迎回访',
    '期待回访',
    '可以来康康我的吗'
]

# 通用评论
GENERAL_COMMENTS = [
    '写的不错，' + random.choice(COMMENT_END_MESSAGES),
    '博主的文章实在是写得太好了, ' + random.choice(COMMENT_END_MESSAGES),
    '看完博主的文章，我的心情竟是久久不能平复，正如老子所云：大音希声，大象希形。',
    '到此一游',
    '值得学习，' + random.choice(COMMENT_END_MESSAGES),
    '文采四溢，大佬这是被耽搁的文学家啊！',
    '学到了，收藏一波~',
    '来大佬博客串串门，学习学习',
    '受益匪浅',
    '创作不易，给你打气，继续创作优质好文！',
    '代码之路任重道远，愿跟博主努力学习之',
    '干货满满，很详细，评论占个坑。欢迎一起交流'
]

# 评论文章数量
COMMENT_ARTICLE_NUMS = 6

# 评论间隔 [1, 3) 分钟
# COMMENT_INTERVAL = (60, 3*60)

# 测试 [3, 5) 秒
COMMENT_INTERVAL = (3, 5)


def main():
    print(SCREEN_X, SCREEN_Y)


if __name__ == '__main__':
    main()
