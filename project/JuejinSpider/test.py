# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { test 语法 }
# @Date: 2021/05/15 17:03


def main():
    li = [
        {'name': 'hui', 'age': 21}
    ]

    if 'hui' in li:
        print('name 存在')
    else:
        print('不存在')

    value = 'hui'
    ret = [item['age'] for item in li if item['name'] == 'hui']
    ret_li = list(filter(lambda item: item['name'] == 'hui', li))
    print(ret)
    print(ret_li)


if __name__ == '__main__':
    main()
