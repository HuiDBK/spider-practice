# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 掘金爬虫主入口模块 }
# @Date: 2021/05/15 15:59
from jue import JueSpider, JueAutoComment
from setting import LoginMode, ArticleCategory


def jue_auto_comment():
    """
    启动掘金自动评论
    :return:
    """
    try:
        jue = JueAutoComment(
            category=ArticleCategory.BACKEND,
            tag='Java',
            headless=True,
            login_mode=LoginMode.COOKIES,
        )
        jue.run(search_mode=True)

    except Exception as e:
        print('未知错误')
        print(e)


def main():
    jue_auto_comment()


if __name__ == '__main__':
    main()
