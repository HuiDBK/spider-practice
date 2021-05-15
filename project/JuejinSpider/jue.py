# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 掘金爬虫模块 }
# @Date: 2021/05/10 11:17
import os
import sys
import json
import time
import utils
import jieba
import random
import setting
import requests
from lxml import etree
from pprint import pprint
from selenium import webdriver
from setting import CHROME_WEB_DRIVER
from setting import LoginMode, ArticleCategory, ArticleSort


class JueSpider(object):
    """掘金爬虫基类"""

    author = setting.AUTHOR
    account = setting.ACCOUNT
    password = setting.PASSWORD

    # 掘金首页url
    start_url = 'https://juejin.cn'

    # 个人首页url
    uuid = '817692384431470'
    user_home_url = f'https://juejin.cn/user/{uuid}'

    # 掘金标签查询url
    tag_query_url = 'https://api.juejin.cn/tag_api/v1/query_tag_list'

    def __init__(self, headless=False, login_mode=LoginMode.DEFAULT):
        """
        掘金爬虫基类初始化
        :param headless: 是否开启无界面模式 True无界面, False有界面
        :param login_mode:
            登录模式: LoginMode.ACCOUNT 代表用账号密码登录, 无视headless参数, 默认有窗口、
                     LoginMode.COOKIES 使用 cookies 登录
                     LoginMode.REQUEST 使用 requests 发送 http 请求登录
        """
        self.headless = headless
        self.login_mode = login_mode
        self.login_status = False
        self.session = requests.session()

        # 用于保存通过 LoginMode.REQUEST 的登录模式获取出来的数据
        self.html_data = None

        if self.login_mode != LoginMode.REQUEST:
            # 加载浏览器驱动
            self.browser = self.init_driver(is_headless=headless)

            # 设置隐式等待时间
            self.browser.implicitly_wait(setting.IMPLICIT_WAIT_TIME)

    def init_driver(self, is_headless=False):
        """
        初始化浏览器驱动
        :param is_headless: 设置浏览器驱动是否带界面 True无界面  False带界面
        :return:
        """
        options = None

        # 如果设置无界面模式并且登录模式不是账号密码的方式
        # 才配置无界面参数，否则带界面
        if is_headless and self.login_mode != LoginMode.ACCOUNT:
            options = self.get_headless_options()

        browser = webdriver.Chrome(
            executable_path=CHROME_WEB_DRIVER,
            chrome_options=options
        )
        return browser

    @staticmethod
    def get_headless_options():
        """
        获取谷歌浏览器驱动无头模式配置
        :return:
        """
        options = webdriver.ChromeOptions()  # 创建一个配置对象
        screen_size = f'{setting.SCREEN_X}x{setting.SCREEN_Y}'
        options.add_argument(f'window-size={screen_size}')  # 指定浏览器分辨率
        options.add_argument("--headless")  # 开启无界面模式
        options.add_argument("--disable-gpu")  # 禁用gpu
        return options

    def close_advert(self):
        """
        关闭掘金中的广告
        :return:
        """
        try:
            advert_btn = self.browser.find_element_by_xpath('//div[@class="ion-close"]')
            advert_btn.click()
        except Exception as e:
            print(e)

    @property
    def cookies(self):
        """
        获取浏览器 cookies
        :return:
        """
        return self.browser.get_cookies()

    @cookies.setter
    def cookies(self, cookie_list):
        """
        设置浏览器 cookie
        :param cookie_list: cookie列表
        :return:
        """
        self.browser.delete_all_cookies()

        user_cookies = cookie_list
        # 去除过期时间
        for cookie_item in user_cookies:
            if 'expiry' in cookie_item:
                del cookie_item['expiry']

        for cookie_dict in user_cookies:
            self.browser.add_cookie(cookie_dict)

    def slide_verify(self):
        """
        登录滑块验证
        :return:
        """
        # 暂时人工操作
        time.sleep(5)

        # 检查登录状态
        login_status = self.check_login()

        return login_status

        # # 获取验证背景图
        # captcha_verify_img = self.browser.find_element_by_xpath('//img[@id="captcha-verify-image"]')
        # bg_url = captcha_verify_img.get_attribute('src')
        # bg_img_bytes = requests.get(bg_url).content
        #
        # # 获取缺口图片
        # slide_img_btn = self.browser.find_element_by_xpath('//img[contains(@class, "captcha_verify_img_slide")]')
        # slide_img_url = slide_img_btn.get_attribute('src')
        # slide_img_bytes = requests.get(slide_img_url).content
        #
        # # 由于网页上的是按比例缩小的图，因此我们要修改图片大小，还原回去
        # new_size = (340, 212)
        # bg_img = Image.open(BytesIO(bg_img_bytes))
        # bg_img = bg_img.resize(new_size, Image.ANTIALIAS)
        #
        # new_size = (68, 68)
        # slide_img = Image.open(BytesIO(slide_img_bytes))
        # slide_img = slide_img.resize(new_size, Image.ANTIALIAS)
        #
        # bg_img_path = 'bg.png'
        # slide_img_path = 'slide.png'

        # bg_img.save(bg_img_path)
        # slide_img.save(slide_img_path)

    def get_user_profile(self):
        """
        获取掘金个人首页信息
        :return: user_dict
        """
        self.browser.maximize_window()
        self.browser.get(self.user_home_url)
        self.close_advert()
        time.sleep(3)
        username = self.browser.find_element_by_xpath('//meta[@itemprop="name"]').get_attribute('content')
        job_title = self.browser.find_element_by_xpath('//meta[@itemprop="jobTitle"]').get_attribute('content')
        profile = self.browser.find_element_by_xpath('//div[@class="intro"]/span').text

        # 获取点赞、阅读量、掘力值信息
        article_data_els = self.browser.find_elements_by_xpath(
            '//div[@class="block-body"]/div/span/span[@class="count"]')
        likes = article_data_els[0].text
        reads = article_data_els[1].text
        juejin_power = self.browser.find_element_by_xpath('//a/span/span[@class="count"]').text

        user_dict = {
            'username': username,
            'job_title': job_title,
            'profile': profile,
            'likes': likes,
            'reads': reads,
            'juejin_power': juejin_power,
        }
        pprint(user_dict)
        return user_dict

    def get_all_category(self):
        """
        获取掘金首页文章所有的大分类
        :return: category_list
        """
        category_list = list()
        category_els_xpath = '//nav[@class="view-nav"]/div/a[@class="nav-item" or @class="nav-item active"]'

        if self.login_mode == LoginMode.REQUEST:
            # 写入文件中用于提取数据分析使用
            with open('data/jue_home.html', mode='w', encoding='utf-8') as f:
                f.write(self.html_data.decode())

            home_html = etree.HTML(self.html_data.decode())
            category_els = home_html.xpath(category_els_xpath)
        else:
            category_els = self.browser.find_elements_by_xpath(category_els_xpath)

        for category_el in category_els:
            if self.login_mode == LoginMode.REQUEST:
                category_title = category_el.xpath('./div[@class="category-popover-box"]/text()')[0]
                category_title = category_title.lower().strip()
                category_link = category_el.xpath('./@href')[0]
                category_link = self.start_url + category_link
            else:
                category_title = category_el.text
                category_link = category_el.get_attribute('href')
            category_dict = {
                'category_title': category_title or None,
                'category_link': category_link or None
            }
            # print(category_dict)
            category_list.append(category_dict)
        print(f'category_count={len(category_list)}')
        return category_list

    def get_all_tag(self):
        """
        登录后获取掘金文章所有标签 tag
        :return:
        """
        # 组织request需要的cookies数据
        cookies_list = self.get_local_cookies()
        cookies = {cookie_dict['name']: cookie_dict['value'] for cookie_dict in cookies_list}

        headers = {
            'User-Agent': random.choice(setting.UA_LIST),
            'Content-Type': 'application/json',
            'referer': self.start_url,
        }

        # 组织请求参数, 查询标签数量
        request_payload = {'sort_type': 1, 'cursor': '0', 'limit': 20}
        request_payload = json.dumps(request_payload)
        response = self.session.post(
            self.tag_query_url,
            headers=headers,
            data=request_payload,
            cookies=cookies
        )
        tag_content_json = response.content.decode()
        tag_count = json.loads(tag_content_json).get('count')

        # 再根据标签数量再去获取所有标签
        request_payload = {'sort_type': 1, 'cursor': '0', 'limit': tag_count}
        request_payload = json.dumps(request_payload)
        response = self.session.post(
            self.tag_query_url,
            headers=headers,
            data=request_payload,
        )

        tag_content_json = response.content.decode()
        all_tag_list = json.loads(tag_content_json).get('data', [])

        # 把标签数据存入文件中
        with open(setting.TAG_JSON, mode='w', encoding='utf-8') as f:
            json.dump(all_tag_list, f, ensure_ascii=False, indent=2)

        tag_list = list()
        for tag_dict in all_tag_list:
            tag_id = tag_dict['tag'].get('tag_id')
            tag_name = tag_dict['tag'].get('tag_name')
            post_article_count = tag_dict['tag'].get('post_article_count')
            concern_user_count = tag_dict['tag'].get('concern_user_count')

            tag_dict = {
                'tag_id': tag_id,
                'tag_name': tag_name,
                'post_article_count': post_article_count,
                'concern_user_count': concern_user_count,
            }
            tag_list.append(tag_dict)

        print(f'tag_count={len(tag_list)}')
        return tag_list

    def get_local_cookies(self):
        """
        获取本地文件中用户 cookies
        :return: cookie_list
        """
        # 从文件中获取登录cookie的数据
        utils.make_file(setting.COOKIES_JSON)
        with open(setting.COOKIES_JSON, mode='r', encoding='utf-8') as f:
            cookies_json = f.read()

        cookie_list = list()
        if cookies_json.strip():
            cookie_dict = json.loads(cookies_json)
            # 获取对应账号的cookie
            cookie_list = cookie_dict.get(self.account, [])

        return cookie_list

    def _account_login(self):
        """
        通过账号密码模拟登陆掘金
        :return: response.content
        """
        login_btn = self.browser.find_element_by_xpath('//button[@class="login-button"]')
        login_btn.click()

        other_login_btn = self.browser.find_element_by_xpath('//div[@class="prompt-box"]/span')
        other_login_btn.click()

        account_input = self.browser.find_element_by_xpath('//input[@name="loginPhoneOrEmail"]')
        password_input = self.browser.find_element_by_xpath('//input[@name="loginPassword"]')

        account_input.send_keys(self.account)
        password_input.send_keys(self.password)

        login_btn = self.browser.find_element_by_xpath('//button[@class="btn"]')
        login_btn.click()

        # 记录登录状态
        login_status = self.slide_verify()
        self.login_status = login_status

    def _request_login(self):
        """
        通过 requests 发送登录请求
        :return: 首页内容
        """
        cookies_list = self.get_local_cookies()
        if len(cookies_list) == 0:
            print(f'{self.author}:{self.account} 没有成功登录过，无法获取cookie数据')
            print('请把登录模式改用成 LoginMode.ACCOUNT, 获取登录cookie数据后再启用 LoginMode.REQUEST')
            return

        # 组织request需要的数据
        headers = {
            'User-Agent': random.choice(setting.UA_LIST),
            'origin': self.start_url,
            'referer': self.start_url,
        }

        cookies = {cookie_dict['name']: cookie_dict['value'] for cookie_dict in cookies_list}
        response = self.session.get(self.start_url, headers=headers, cookies=cookies)

        html_str = response.content.decode()
        if self.author in html_str:
            self.login_status = True
        return response.content

    def _cookie_login(self):
        """
        使用cookie登录
        :return:
        """
        cookies_list = self.get_local_cookies()
        if len(cookies_list) == 0:
            print(f'{self.author}:{self.account} 没有成功登录过，无法获取cookie数据')
            print('请把登录模式改用成 LoginMode.ACCOUNT, 获取登录cookie数据后再启用 LoginMode.COOKIES')
            return

        self.cookies = cookies_list
        self.browser.refresh()
        login_status = self.check_login()
        self.login_status = login_status

    def check_login(self):
        """
        检查登录状态
        :return:
        """
        # 直到作者头像显示出来，才算登录成功
        # 如果20秒还没有定位到元素，认为未登录
        try:
            self.browser.find_element_by_xpath('//li[@class="nav-item menu"]/img')
            return True
        except Exception:
            print('登录失败，超时！')
            return False

    def login(self):
        """
        模拟掘金登录
        :return:
        """
        # 选择登陆方式
        if self.login_mode == LoginMode.ACCOUNT:
            self.browser.delete_all_cookies()
            self._account_login()

            # 登录成功保存登录后的cookies, 用于后续使用
            if self.login_status is True:
                utils.make_file(setting.COOKIES_JSON)

                # 先读出cookie, 新增后再写, 保留之前的cookie
                cookie_dict = dict()
                with open(setting.COOKIES_JSON, mode='r', encoding='utf-8') as f:
                    cookie_json = f.read()

                    if cookie_json.strip():
                        cookie_dict = json.loads(cookie_json)

                with open(setting.COOKIES_JSON, mode='w', encoding='utf-8') as f:
                    # 先获取浏览器cookie
                    cookies = self.cookies
                    cookie_dict[self.account] = cookies
                    json.dump(cookie_dict, f, ensure_ascii=False, indent=2)

        elif self.login_mode == LoginMode.COOKIES:
            self._cookie_login()
        elif self.login_mode == LoginMode.REQUEST:
            response = self._request_login()
            self.html_data = response

        if self.login_status is True:
            print(f'{self.author}:{self.account} 登录成功')
        else:
            print(f'{self.author}:{self.account} 登录失败')

    def jue_home_page(self):
        """
        访问掘金首页
        :return:
        """
        if self.login_mode != LoginMode.REQUEST:
            self.browser.maximize_window()
            self.browser.get(self.start_url)
            self.close_advert()

    def run(self):
        self.jue_home_page()
        self.login()
        if self.login_status is True:
            self.get_all_category()
            self.get_all_tag()
        self.quit()

    def quit(self):
        """
        退出
        :return:
        """
        self.session.close()
        if self.login_mode != LoginMode.REQUEST:
            time.sleep(3)
            self.browser.quit()


class JueAutoComment(JueSpider):
    """掘金自动评论类"""

    def __init__(self, category=ArticleCategory.BACKEND, tag='python',
                 headless=False, login_mode=LoginMode.ACCOUNT):
        """
        掘金自动评论配置初始化
        :param category: 评论文章的分类
        :param tag: 评论文章的标签类型
        :param headless: 是否开启无界面模式 True无界面, False有界面
        :param login_mode:
            登录模式: LoginMode.ACCOUNT 代表用账号密码登录, 无视headless参数, 默认有窗口、
                     LoginMode.COOKIES 使用 cookies 登录
                     LoginMode.REQUEST 使用 requests 发送 http 请求登录
        """
        super().__init__(headless, login_mode)
        self.category = category
        self.tag = tag.lower()

        # 掘金搜索文章的url
        self.search_url = f'https://juejin.cn/search?query={self.tag}'

        # 默认文章分类的url, 如果文章大分类或标签找不到则使用默认url获取信息
        self.default_category_url = 'https://juejin.cn/backend/python'

    def get_index_content(self):
        """
        获取首页指定标签的文章数据
        :return: article_infos
        """
        # 根据分类、标签获取文章url
        category_list = self.get_all_category()
        tag_list = self.get_all_tag()

        """
        eg: 文章分类的每一项 {'category_title': '后端', 'category_link': 'https://juejin.cn/backend'}
        eg: 所有标签的每一项 
            {
                'tag_id': tag_id,
                'tag_name': tag_name,
                'post_article_count': post_article_count,
                'concern_user_count': concern_user_count,
            }
        """
        category_ret = [category_item['category_link'] for category_item in category_list
                        if category_item['category_title'] == self.category]

        tag_ret = [tag_item['tag_name'].lower() for tag_item in tag_list]

        if len(category_ret) == 0 or self.tag not in tag_ret:
            self.browser.minimize_window()
            print('==='*20)
            print(f'不存在 {self.category} 该分类下的 {self.tag} 标签')
            print(f'是否使用默认文章分类url: {self.default_category_url}')
            input_ret = input('y/n: ')
            if input_ret.lower() == 'y':
                # 使用默认文章分类url获取
                self.browser.maximize_window()
                self.browser.get(self.default_category_url)
            else:
                self.quit()
                sys.exit(0)
        else:
            # 存在
            category_url = category_ret[0]
            self.browser.get(category_url + '/' + self.tag)

        time.sleep(3)

        article_infos = self._get_article_content()
        return article_infos

    def get_search_content(self, sort=ArticleSort.DEFAULT):
        """
        获取搜索指定标签的文章数据
        :param sort: 文章排序规则, 默认使用setting.ArticleSort下的默认配置
        :return: article_infos
        """
        self.browser.get(self.search_url)
        time.sleep(3)

        # 根据指定的排序规则进行元素定位
        try:
            # 综合排序不用点击, 掘金默认是综合排序
            if sort != ArticleSort.COMPREHENSIVE:
                sort_btn = self.browser.find_element_by_xpath(
                    f'//nav/ul[@class="nav-list left"]/li/a[contains(text(), "{sort}")]')
                sort_btn.click()
                time.sleep(3)
        except Exception as e:
            print(e)
            print("文章排序出错")

        article_infos = self._get_article_content(search_mode=True)

        return article_infos

    def _get_article_content(self, search_mode=False):
        """
        根据 tag类型 获取文章相关数据
        :param: search_mode: 文章搜索模式, True 通过搜索框搜索的文章, False 首页文章
        :return: article_infos
        """
        # 定位到文章内容元素
        content_box_els = self.browser.find_elements_by_xpath('//li[@class="item"]//div[@class="content-box"]')

        print(f'共获取到文章 {len(content_box_els)} 篇')

        # 遍历获取文章信息
        article_infos = list()
        for i, content_box in enumerate(content_box_els):
            article_author = content_box.find_element_by_xpath('.//div[@class="user-popover-box"]').text
            article_title = content_box.find_element_by_xpath('.//div[contains(@class, "title-row")]/a').text
            article_link = content_box.find_element_by_xpath(
                './/div[contains(@class, "title-row")]/a').get_attribute('href')

            if search_mode is True:
                # 通过搜索框的搜索出来的文章发布日期 xpath 不一样
                publish_date = content_box.find_element_by_xpath(
                    './/div[contains(@class, "meta-row")]/ul/li[@class="item"]').text
            else:
                publish_date = content_box.find_element_by_xpath('.//div[contains(@class, "date")]').text

            like_btn = content_box.find_element_by_xpath('.//li[contains(@class, "item like")]')
            comment_btn = content_box.find_element_by_xpath('.//li[contains(@class, "item comment")]')

            comment_nums = comment_btn.text.strip()

            # 文章没有评论数据的为值带有 【评论】 二字 或者为空值
            if '评论' in comment_nums or comment_nums == '':
                comment_nums = 0

            # 组织文章数据
            article_dict = {
                'article_author': article_author or None,
                'article_title': article_title,
                'article_link': article_link,
                'publish_date': publish_date or None,
                'likes': like_btn.text or 0,
                'comments': comment_nums or 0,
            }

            article_infos.append(article_dict)

            # 边滑动滚动条边获取数据
            js = f'window.scrollTo(0, {i * 182})'
            self.browser.execute_script(js)
            time.sleep(0.5)

            # pprint(article_dict)
            # print(i)

        return article_infos

    @staticmethod
    def generate_comment(article_dict: dict):
        """
        根据文章信息自动生成评论消息
        :param article_dict: 文章信息
        :return:
        """
        """
        article_dict = {
            'article_author': article_author,
            'article_title': article_title,
            'article_link': article_link,
            'publish_date': publish_date,
            'likes': like_btn.text,
            'comments': comment_btn.text,
            'article_content': article_content
        }
        """
        article_content = article_dict.get('article_content')

        # 文章中词语出现的频率
        words = list()
        if article_content is not None:
            words = jieba.lcut(article_content)

        # 通过键值对的形式存储词语及其出现的次数
        counts = {}

        for word in words:
            if len(word) == 1:  # 单个词语不计算在内
                continue
            else:
                counts[word] = counts.get(word, 0) + 1  # 遍历所有词语，每出现一次其对应的值加 1

        items = list(counts.items())  # 将键值对转换成列表
        items.sort(key=lambda x: x[1], reverse=True)  # 根据词语出现的次数进行从大到小排序

        word, count = None, None
        if len(items) > 0:
            word, count = items[0]

        # word 是文章中出现频率最高的词语
        # print(word, count)
        # comment_msg = word + ', ' + end_msg

        comment_msg = random.choice(setting.GENERAL_COMMENTS)
        return comment_msg

    def article_likes(self, url=None):
        """
        给指定url的文章点赞
        :param url: 文章 url, 默认为 None
            为 None 根据浏览器当前url的文章进行点赞, 有值则根据指定的url进行点赞
        :return:
        """
        if url is not None:
            self.browser.get(url)
        like_btn = self.browser.find_element_by_xpath('//div[contains(@class, "like-btn")]')
        like_btn.click()

    def send_comment_msg(self, comment_msg, url=None):
        """
        给指定url文章发送评论信息
        :param comment_msg: 评论的信息
        :param url: 文章 url, 默认为 None
            为 None 根据浏览器当前url的文章进行评论, 有值则根据指定的url进行评论
        :return:
        """
        if url is not None:
            self.browser.get(url)

        # 点击评论按钮
        comment_btn = self.browser.find_element_by_xpath('//div[contains(@class, "comment-btn")]')
        comment_btn.click()

        # 获取评论 input
        comment_input = self.browser.find_element_by_xpath('//div[@class="rich-input empty"]')
        comment_input.click()
        comment_input.send_keys(comment_msg)
        time.sleep(2)

        # 点击评论提交按钮
        comment_sub_btn = self.browser.find_element_by_xpath('//button[@class="submit-btn"]')
        # comment_sub_btn.click()

    def auto_comment(self, article_infos: list):
        """
        自动评论
        :param article_infos: 文章列表
        :return:
        """
        """
        每一项展示
        article_infos -> item
        article_dict = {
            'article_author': article_author,
            'article_title': article_title,
            'article_link': article_link,
            'publish_date': publish_date,
            'likes': like_btn.text,
            'comments': comment_btn.text,
        }
        """

        # 随机打乱文章
        random.shuffle(article_infos)

        utils.make_file(setting.COMMENTED_JSON)

        # 获取已经评论过的文章
        user_commented_dict = dict()
        with open(setting.COMMENTED_JSON, mode='r', encoding='utf-8') as f:
            article_json = f.read()

        if article_json.strip():
            user_commented_dict = json.loads(article_json)

        # 获取对应账号评论的文章
        commented_articles = user_commented_dict.get(self.account, [])

        # 随机跳转到6篇文章进行评论, 随机评论间隔 [1, 10) 分钟
        count = 0
        for article_dict in article_infos:

            article_link = article_dict['article_link']

            # 获取已评论链接
            commented_links = [article_info['article_link'] for article_info in commented_articles]

            if article_link in commented_links:
                print(article_dict['article_title'])
                print(article_link)
                print('已评论过了\n')
                continue

            if article_dict['article_author'] == self.author:
                print('自己的文章不评论\n')
                continue

            # 给文章点赞
            try:
                # self.article_likes()
                pass
            except Exception as e:
                print('点赞文章出错')

            # 获取文章详细内容
            try:
                article_content = self.get_blog_content(article_link)
                article_dict['article_content'] = article_content
            except Exception as e:
                article_dict['article_content'] = None
                print('获取文章详细内容出错')
                print(e)

            # 分析文章数据并生成评论消息
            comment_msg = self.generate_comment(article_dict)
            self.send_comment_msg(comment_msg)

            print(article_dict['article_title'])
            print(comment_msg)
            print('\n')

            # 每评论一次随机等待, 最后一次不等待
            if count != setting.COMMENT_ARTICLE_NUMS:
                start = setting.COMMENT_INTERVAL[0]
                end = setting.COMMENT_INTERVAL[1]
                time.sleep(random.randint(start, end))

            # 把评论过的文章放入总评论文章列表，为以后去重使用
            commented_article_dict = {
                'article_title': article_dict['article_title'],
                'article_link': article_dict['article_link']
            }
            commented_articles.append(commented_article_dict)
            count = count + 1

            if count >= setting.COMMENT_ARTICLE_NUMS:
                break

        # 每一个账号对应不同的评论过的文章
        user_commented_dict[self.account] = commented_articles

        # 记录已经评论过的文章
        # with open(setting.COMMENTED_JSON, 'w', encoding='utf-8') as f:
        #     json.dump(user_commented_dict, f, ensure_ascii=False, indent=2)

    def get_blog_content(self, url=None):
        """
        获取文章内容
        :param url: 文章 url, 默认为 None
            为 None 根据浏览器当前url的文章进行获取, 有值则根据指定的url进行获取
        :return:
        """

        if url is not None:
            self.browser.get(url)
            time.sleep(3)
        article_style = self.browser.find_element_by_xpath('//div[@class="markdown-body"]/style').text
        article_content = self.browser.find_element_by_xpath('//div[@class="markdown-body"]').text
        # 去除文章内容的 style样式 获取正文数据
        article_content = article_content.replace(article_style, '')
        return article_content

    def run(self, search_mode=False):
        """
        运行掘金自动评论
        :param search_mode: 搜索模式, 默认False获取首页数据, 如果True则通过搜索框进行获取数据
        :return:
        """
        self.jue_home_page()
        self.login()
        if self.login_status is True:
            if search_mode is True:
                article_infos = self.get_search_content()
            else:
                article_infos = self.get_index_content()
            self.auto_comment(article_infos)
        self.quit()


def jue_spider_test():
    jue = JueSpider(login_mode=LoginMode.REQUEST)
    # jue.get_user_profile()
    jue.run()


def jue_comment_test():
    jue = JueAutoComment(
        category='后端',
        tag='Java',
        headless=False,
        login_mode=LoginMode.COOKIES,
    )
    jue.run(search_mode=True)


def main():
    # jue_spider_test()
    jue_comment_test()


if __name__ == '__main__':
    main()
