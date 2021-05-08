"""
Author: Hui
Desc: { 人民网夜读文案信息爬取 }
"""
import os
import json
import time
import random
import requests
import threading
from lxml import etree

# 请求头Agent信息
AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) "
    "Chrome/24.0.1309.0 Safari/537.17",
    "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
]


class PeopleNight(object):

    # 文件保存路径
    JSON_FILE = f'json/night_{int(time.time())}.json'
    DATA_DIR = 'data'

    # 爬取数量（爬取终止条件还未实现）
    CRAWL_NUM = 12

    def __init__(self):
        self.start_url = 'https://mp.weixin.qq.com/s/bYJAsb6R2aZZPTJPqUQDBQ'
        self.current_url = self.start_url

        # 获取音频资源url
        self.res_url = 'https://res.wx.qq.com/voice/getvoice?'
        self.headers = {
            'User-Agent': random.choice(AGENTS)
        }

        # 所有夜读url列表用于去重
        self.all_url_list = [self.start_url]
        # 夜读url调度队列
        self.url_queue = [self.start_url]

        # 夜读数据列表
        self.data_list = list()

        # 记录当前进度
        self._progress = 0

    @property
    def progress(self):
        """
        计算爬虫当前进度
        :return:
        """
        cur_progress = str(self._progress / len(self.data_list) * 100)[:5] + '%'
        return cur_progress

    def get_data(self, url):
        """
        获取人民网夜读数据
        :param: url: 夜读url
        :return:
        """
        self.current_url = url
        response = requests.get(url, headers=self.headers)
        return response.content

    def parse_data(self, data):
        """
        解析人民网夜读数据, 并提取文章中往期推荐夜读 url
        :param data: 人民网夜读响应数据
        :return: night_info_dict
        """

        html = etree.HTML(data.decode())

        # 获取夜读标题
        title = html.xpath('//h2[@id="activity-name"]/text()')[0].strip()

        # 获取音频url
        media_id = html.xpath('//mpvoice/@voice_encode_fileid')[0]
        voice_url = self.res_url + 'mediaid=' + media_id

        # 获取夜读文案内容 ( 有些文案在 section标签下 )
        el_list = html.xpath('//p/span[@style] | //section[contains(@style, "line-height")]/span')

        # 由于文案中文字有些加粗的样式，不能直接用text()获取，因此改用 string(.)
        # string(.)不能直接与之前的xpath一起使用，需要在之前对象的基础上使用
        night_content = ''
        for span in el_list:
            paragraph = span.xpath('string(.)')
            # 拼接每一段落
            if paragraph.strip():
                night_content = night_content + paragraph + '\n'

        # 获取夜读图片
        xpath_express = '//p/img[contains(@class, "rich_pages")]/@data-src | ' \
                        '//section/img[contains(@class, "rich_pages") and @data-type="jpeg"]/@data-src'
        img_urls = html.xpath(xpath_express)

        # 获取往期推荐夜读url, 并加入url任务队列中
        night_urls = html.xpath('//section/a/@href')
        for url in night_urls:
            # 由于 url_queue 需要pop来取url，pop会删除url
            # 文章如果出现了之前解析过的url两遍以上，则会重复解析
            # 因此用一个总集合来保存所有解析过的url
            if url not in self.all_url_list:
                self.all_url_list.append(url)
                self.url_queue.append(url)

        # 封装夜读数据
        night_info_dict = {
            'title': title,
            'night_url': self.current_url,
            'voice_url': voice_url,
            'night_content': night_content,
            'img_urls': img_urls,
        }
        # from pprint import pprint
        # pprint(night_info_dict)

        return night_info_dict

    def _save_bytes(self, url, save_path):
        """
        保存字节类型数据
        :param url: 网址
        :param save_path: 保存路径
        :return:
        """
        response = requests.get(url, headers=self.headers)
        with open(save_path, mode='wb') as f:
            f.write(response.content)

    def save_data_task(self, data_list):
        """
        保存数据 (线程任务)
        :param data_list: 数据列表
        :return:
        """
        for night_dict in data_list:
            # 创建每个夜读标题目录
            title = night_dict['title'].split('|')[1].strip()
            title_dir = self.DATA_DIR + '/' + title
            os.makedirs(title_dir, exist_ok=True)

            # 保存音频
            voice_url = night_dict['voice_url']
            audio_file = title_dir + '/' + 'audio.mp3'
            self._save_bytes(voice_url, audio_file)

            # 保存文案
            night_content = night_dict['night_content']
            text_file = title_dir + '/' + title + '.txt'
            with open(text_file, mode='w', encoding='utf-8') as f:
                night_content = title + '\n' + night_content
                f.write(night_content)

            # 保存图片
            img_urls = night_dict['img_urls']
            for num, img_url in enumerate(img_urls):
                img_file = title_dir + '/' + f'night_{str(num).zfill(2)}' + '.jpg'
                self._save_bytes(img_url, img_file)

            self._progress = self._progress + 1

    def save_data(self):
        """
        保存夜读信息数据
        :return:
        """
        """
        # 封装夜读数据
        night_info_dict = {
            'title': title,
            'night_url': self.current_url,
            'voice_url': voice_url,
            'night_content': night_content,
            'img_urls': img_urls,
        }
        """
        # 把全部数据保存到json文件中
        with open(self.JSON_FILE, mode='a', encoding='utf-8') as file:
            json.dump(self.data_list, file, ensure_ascii=False, indent=2)

        # 把数据分成10分，使用协程保存数据
        part = 10
        data_list = self.cut_list(self.data_list, part)
        for data in data_list:
            save_thread = threading.Thread(target=self.save_data_task, args=(data,))
            save_thread.start()

    @staticmethod
    def cut_list(ls, part):
        """
        把列表切分为 part 份
        :param ls: 列表
        :param part: 份量
        :return: ls[start:end]
        """
        # 计算出每份的大小
        size = len(ls) // part

        for i in range(part):
            start = size * i
            end = size * (i + 1)
            if i == part - 1:
                # 把剩余的给最后一份
                end = len(ls)
            yield ls[start:end]

    def run(self):
        count = 0

        while True:
            if len(self.url_queue) > 0:
                url = self.url_queue.pop()
                data = self.get_data(url)
                night_info_dict = self.parse_data(data)
                self.data_list.append(night_info_dict)
                count = count + 1

            print(f'\r爬取夜读文案数量: {count}', end='')
            if count >= self.CRAWL_NUM:
                break

        self.save_data()


def main():
    night = PeopleNight()
    night.run()

    while True:
        time.sleep(0.5)
        print('\r当前进度: ', night.progress, end='')
        if '100' in night.progress:
            break


if __name__ == '__main__':
    main()
