"""
Author: Hui
Desc: { 青年大学习的答案爬取 }
"""
import os
import json
import gevent
from lxml import etree
from gevent import monkey

monkey.patch_all()
import request


class YoungStudy(object):
    save_path = 'YoungStudyAnswer.json'

    def __init__(self):
        self.domain = 'http://www.quxiu.com'
        self.url = 'http://www.quxiu.com/news/1692867.html'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/37.0.2049.0 Safari/537.36'
        }

        self.answer_list = self.load_answer_data()

    def load_answer_data(self):
        """
        先加载答案数据，好动态的添加新数据
        :return:
        """
        answers = list()
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r', encoding='utf-8') as f:
                ret = f.read()
                if ret:
                    answers = json.loads(ret)
                return answers
        else:
            return answers

    def get_data(self, url):
        """
        获取url响应的数据
        """
        response = request.get(url, headers=self.headers)
        return response.content

    def parse_data(self, data):
        """
        解析首页，并获取所有答案的url
        :param data:
        :return: answer_urls
        """
        # print(data)
        data = data.decode()
        html = etree.HTML(data)
        hrefs = html.xpath("//td/a/@href")
        answer_urls = [self.domain + href for href in hrefs]
        return set(answer_urls)

    def parse_answer_data(self, data, url):
        """
        解析答案数据
        :param url: 当前解析的url，用于数据的封装
        :param data:
        :return: answer_dict
        """
        html = etree.HTML(data.decode())
        title = html.xpath('//title/text()')[0]
        create_date = html.xpath("//p[@class='source']/span[1]/text()")[0]
        # eg: 发布时间：2021-4-17 12:53:23
        create_date = create_date.split('：')[1]

        # 获取答案详情
        el_list = html.xpath("//div[@class='nawContent mb20']/p[position()>2]")
        answer = ''
        for el in el_list:
            # text()不能取到内嵌标签里的文本数据，改用 string(.)
            answer += el.xpath('string(.)') + '\n'
        # print(answer)

        # 将答案信息封装在字典中
        answer_dict = dict()
        answer_dict['url'] = url
        answer_dict['title'] = title
        answer_dict['create_date'] = create_date
        answer_dict['answer'] = answer
        print(answer_dict)
        self.answer_list.append(answer_dict)
        return answer_dict

    def save_data(self):
        """
        把答案数据以 json 的格式保存
        :return:
        """
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.answer_list, f, ensure_ascii=False, indent=2)

    def run(self):
        data = self.get_data(self.url)

        answer_urls = self.parse_data(data)

        print(f'answer_urls: {len(answer_urls)}')
        print(f'answer_list: {len(self.answer_list)}')

        if len(answer_urls) > len(self.answer_list):
            # 说明有新增数据
            task = []

            urls = [item['url'] for item in self.answer_list]
            # 集合求差值获取新的url(提取未解析过的url)
            new_urls = list(set(answer_urls) ^ set(urls))
            print(f'新增url {len(new_urls)} 条')
            for url in new_urls:
                # 给协程gevent添加多任务
                task.append(gevent.spawn(self.get_answer_task, url))

            gevent.joinall(task)
            self.save_data()
        else:
            print(len(answer_urls))
            print("无新增数据")

    def get_answer_task(self, url):
        """
        获取青年大学习答案
        :param url: 答案url
        :return:
        """
        answer_data = self.get_data(url)
        self.parse_answer_data(answer_data, url)

    def get_recent_answer(self):
        """
        获取最近一期答案
        :return:
        """
        print('-+-' * 10 + ' 最近一期答案 ' + '-+-' * 10 + '\n')
        if self.answer_list:
            recent_answer = max(self.answer_list, key=lambda item: item['create_date'])
            print(recent_answer['title'])
            print(recent_answer['create_date'])
            print(recent_answer['url'])
            print(recent_answer['answer'])


def main():
    ys = YoungStudy()
    ys.run()
    ys.get_recent_answer()


if __name__ == '__main__':
    main()
