# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: Hui
# @Desc: { 提供便捷功能工具模块 }
# @Date: 2021/05/12 14:06
import os
import win32api
import win32gui
import win32con
import win32print


def make_file(file_path):
    """
    创建文件, 如果文件存在返回True, 反之False
    :return:
    """
    is_exists = True
    if not os.path.exists(file_path):
        file = open(file_path, mode='w', encoding='utf-8')
        file.close()
        is_exists = False
    return is_exists


def get_real_screen():
    """获取系统真实的分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h


def get_screen_size():
    """获取系统缩放后的分辨率"""
    w = win32api.GetSystemMetrics(0)
    h = win32api.GetSystemMetrics(1)
    return w, h


def main():
    real_size = get_real_screen()
    screen_size = get_screen_size()
    print('real_screen_size:', real_size)
    print('scale_screen_size:', screen_size)


if __name__ == '__main__':
    main()
