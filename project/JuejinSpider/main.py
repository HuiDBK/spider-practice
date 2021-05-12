# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 利用selenium模拟登陆掘金社区, 并自动评论相关文章 }
# @Date: 2021/05/10 11:17
import os
import json
import time
import utils
import jieba
import random
import setting
from setting import LoginMode
from selenium import webdriver
from setting import CHROME_WEB_DRIVER


def get_headless_options():
    """
    获取浏览器驱动无头模式配置
    :return:
    """
    options = webdriver.ChromeOptions()  # 创建一个配置对象
    screen_size = f'{setting.SCREEN_X}x{setting.SCREEN_Y}'
    options.add_argument(f'window-size={screen_size}')  # 指定浏览器分辨率
    options.add_argument("--headless")  # 开启无界面模式
    options.add_argument("--disable-gpu")  # 禁用gpu
    return options


class JueAutoComment(object):
    """掘金自动评论类"""

    def __init__(self, tag='python', headless=False, login_mode=1):
        """
        掘金自动评论配置初始化
        :param tag: 评论的标签类型
        :param headless: 是否开启无界面模式 True无界面, False有界面
        :param login_mode:
            登录模式: 1 代表用账号密码, 无视headless参数, 默认有窗口、
                     2 使用 cookies
        """
        self.tag = tag
        self.login_mode = login_mode
        self.author = setting.AUTHOR
        self.account = setting.ACCOUNT
        self.password = setting.PASSWORD

        # 掘金首页
        self.start_url = 'https://juejin.cn'

        # 个人标识 uuid
        self.uuid = '817692384431470'

        # 个人首页
        self.user_home_url = f'https://juejin.cn/user/{self.uuid}'

        # 默认分类
        self.default_category = '/backend/Python'

        # 浏览器驱动
        self.browser = self.init_driver(is_headless=headless)

        # 增加隐式等待
        self.browser.implicitly_wait(setting.IMPLICIT_WAIT_TIME)

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
            options = get_headless_options()

        browser = webdriver.Chrome(
            executable_path=CHROME_WEB_DRIVER,
            chrome_options=options
        )
        return browser

    def close_advert(self):
        """
        关闭广告
        :return:
        """
        try:
            advert_btn = self.browser.find_element_by_xpath('//div[@class="ion-close"]')
            advert_btn.click()
        except Exception as e:
            print(e)

    def account_login(self):
        """
        通过账号密码模拟登陆掘金
        :return: response.content
        """
        self.close_advert()

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

        # 滑块验证
        return self.slide_verify()

    def cookie_login(self):
        """
        使用cookie登录
        :return:
        """
        self.close_advert()

        # 从文件中获取登录cookie的数据
        utils.make_file(setting.COOKIES_JSON)
        with open(setting.COOKIES_JSON, mode='r', encoding='utf-8') as f:
            cookies_json = f.read()

        # 标识cookie状态, True可用, False不可用
        cookies_status = False
        if cookies_json.strip():
            cookie_dict = json.loads(cookies_json)
            # 获取对应账号的cookie
            cookie_list = cookie_dict.get(self.account)
            if cookie_list is not None:
                cookies_status = True
                self.cookies = cookie_list

        if cookies_status is False:
            print(f'{self.author}:{self.account} 没有成功登录过，无法获取cookie数据')
            print('请把登录模式改用成 LoginMode.ACCOUNT, 获取登录cookie数据后再启用 LoginMode.COOKIES')
            return False

        self.browser.refresh()
        return self.check_login()

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
        self.browser.get(self.user_home_url)
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

        return user_dict

    def get_python_content(self):
        """
        获取掘金 Python 内容
        :return:
        """
        article_category = 'python'
        return self.get_article_content(article_category)

    def get_article_content(self, category):
        """
        根据文章类型获取相关数据, 目前只支持后端
        :param category: 文章类型
        :return:
        """

        # 根据分类获取文章url
        category = category.lower()
        category_url = setting.BACKEND_CATEGORY.get(category, self.default_category)

        self.browser.get(self.start_url + category_url)

        time.sleep(3)

        content_box_els = self.browser.find_elements_by_xpath('//div[@class="entry-link"]/div[@class="content-box"]')

        print(f'共获取到文章 {len(content_box_els)} 篇')

        # 遍历获取文章信息
        article_infos = list()
        for i, content_box in enumerate(content_box_els):
            article_author = content_box.find_element_by_xpath('.//div[@class="user-popover-box"]').text
            article_title = content_box.find_element_by_xpath('.//div[contains(@class, "title-row")]/a').text
            article_link = content_box.find_element_by_xpath(
                './/div[contains(@class, "title-row")]/a').get_attribute('href')
            # article_link = self.start_url + article_link
            publish_date = content_box.find_element_by_xpath('.//div[contains(@class, "date")]').text

            like_btn = content_box.find_element_by_xpath('.//li[contains(@class, "item like")]')
            comment_btn = content_box.find_element_by_xpath('.//li[contains(@class, "item comment")]')

            comment_nums = comment_btn.text

            # 没评论数据为 【评论二字】
            if comment_btn.text == '评论':
                comment_nums = 0

            article_dict = {
                'article_author': article_author,
                'article_title': article_title,
                'article_link': article_link,
                'publish_date': publish_date,
                'likes': like_btn.text,
                'comments': comment_nums,
            }

            article_infos.append(article_dict)

            # 边滚动边获取数据
            js = f'window.scrollTo(0, {i * 182})'
            self.browser.execute_script(js)
            time.sleep(0.5)

            from pprint import pprint
            pprint(article_dict)
            print(i)

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
        comment_msg = ''
        end_msg = random.choice(setting.COMMENT_END_MESSAGES)

        words = jieba.lcut(article_dict['article_content'])

        # 通过键值对的形式存储词语及其出现的次数
        counts = {}

        for word in words:
            if len(word) == 1:  # 单个词语不计算在内
                continue
            else:
                counts[word] = counts.get(word, 0) + 1  # 遍历所有词语，每出现一次其对应的值加 1

        items = list(counts.items())  # 将键值对转换成列表
        items.sort(key=lambda x: x[1], reverse=True)  # 根据词语出现的次数进行从大到小排序

        word, count = items[0]
        # print(word, count)
        comment_msg = word + ', ' + end_msg

        comment_msg = random.choice(setting.GENERAL_COMMENTS)
        return comment_msg

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

        if not os.path.exists(setting.COMMENTED_JSON):
            f = open(setting.COMMENTED_JSON, mode='w')
            f.close()

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

            self.browser.get(article_link)
            time.sleep(3)

            # 获取文章内容
            article_style = self.browser.find_element_by_xpath('//div[@class="markdown-body"]/style').text
            article_content = self.browser.find_element_by_xpath('//div[@class="markdown-body"]').text

            # 去除样式
            article_content = article_content.replace(article_style, '')

            # print(article_content)

            article_dict['article_content'] = article_content

            # 分析文章数据并生成评论消息
            comment_msg = self.generate_comment(article_dict)

            # 给文章点赞
            like_btn = self.browser.find_element_by_xpath('//div[contains(@class, "like-btn")]')
            like_btn.click()

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
            comment_sub_btn.click()

            print(article_dict['article_title'])
            print(comment_msg)
            print('\n')

            # 每评论一次随机等待
            start = setting.COMMENT_INTERVAL[0]
            end = setting.COMMENT_INTERVAL[1]
            time.sleep(random.randint(start, end))

            # 把评论过的文章放入文件中，为以后去重使用
            commented_article_dict = {
                'article_title': article_dict['article_title'],
                'article_link': article_dict['article_link']
            }

            commented_articles.append(commented_article_dict)
            count = count + 1

            if count >= setting.COMMENT_ARTICLE_NUMS:
                break

        # 每一个账号对应不同的评论过的文章
        user_commented_dict = {
            self.account: commented_articles
        }

        # 记录已经评论过的文章
        with open(setting.COMMENTED_JSON, 'w', encoding='utf-8') as f:
            json.dump(user_commented_dict, f, ensure_ascii=False, indent=2)

        time.sleep(10)

    def _login(self):
        """
        模拟掘金登录
        :return:
        """
        login_status = False

        if self.login_mode == LoginMode.ACCOUNT:
            self.browser.delete_all_cookies()
            login_status = self.account_login()

            # 登录成功保存登录后的cookies, 用于后续使用
            if login_status:
                print(f'{self.author}:{self.account} 登录成功')
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
            login_status = self.cookie_login()
            if login_status:
                print(f'{self.author}:{self.account} 登录成功')

        return login_status

    def run(self):
        self.browser.get(self.start_url)
        self.browser.maximize_window()

        login_status = self._login()

        if not login_status:
            self.quit()
            return

        article_infos = self.get_article_content(self.tag)

        # 自动评论
        self.auto_comment(article_infos)
        self.quit()

    def quit(self):
        time.sleep(3)
        self.browser.quit()


def main():
    try:
        jue = JueAutoComment(
            tag='java',
            headless=False,
            login_mode=LoginMode.ACCOUNT
        )
        jue.run()
    except Exception as e:
        print('未知错误')
        print(e)


if __name__ == '__main__':
    main()
