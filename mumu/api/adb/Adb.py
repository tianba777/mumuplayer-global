#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/7/30 上午8:40
# @Author : wlkjyy
# @File : Adb.py
# @Software: PyCharm
import json
import os.path
import warnings
from typing import Union


import mumu.config as config


class Adb:

    def __init__(self, utils):
        self.utils = utils

    def __run_adb_cmd(self, cmd: str):
        self.utils.set_operate('adb')
        ret_code, retval = self.utils.run_command(['-c', cmd])

        if ret_code == 0:
            return True

        raise RuntimeError(retval or f"adb command failed: {cmd}")

    def get_connect_info(self):
        """
        获取连接信息
        :return: 返回一个包含 ADB 连接信息的字典，或者 (None, None) 如果没有获取到信息。
        """
        self.utils.set_operate("adb")
        ret_code, retval = self.utils.run_command([''])

        if ret_code != 0:
            return None, None

        try:
            data = json.loads(retval)
        except json.JSONDecodeError:
            return None, None

        adb_info = {}
        for key, value in data.items():
            if key == "adb_host" and "adb_port" in data:
                return data["adb_host"], data["adb_port"]

            if not isinstance(value, dict):
                continue

            if 'errcode' in value:
                adb_info[key] = (None, None)
            else:
                adb_info[key] = (value.get("adb_host"), value.get("adb_port"))

        return adb_info if adb_info else (None, None)

    def click(self, x: int, y: int):
        """
            点击(click)
        :param x: 横坐标
        :param y: 纵坐标
        :return:
        """
        return self.__run_adb_cmd(f"shell input tap {x} {y}")

    def swipe(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: int = 500):
        """
            滑动(swipe)
        :param from_x: 起始横坐标
        :param from_y: 起始纵坐标
        :param to_x: 终点横坐标
        :param to_y: 终点纵坐标
        :param duration: 滑动时间
        :return:
        """
        return self.__run_adb_cmd(f"shell input swipe {from_x} {from_y} {to_x} {to_y} {duration}")

    def input_text(self, text: str):
        """
            输入(input)
        :param text: 输入的文本
        :return:
        """
        return self.__run_adb_cmd(f"input_text {text}")

    def key_event(self, key: Union[int, str]):
        """
            按键(keyevent)
        :param key: 键值
        :return:
        """
        return self.__run_adb_cmd(f"shell input keyevent {key}")

    def __connect(self):
        """
            获取可用的连接
        :return:
        """

        self.utils.set_operate("adb")
        ret_code, retval = self.utils.run_command([''])

        if ret_code != 0:
            return

        try:
            data = json.loads(retval)
        except json.JSONDecodeError:
            return

        for key, value in data.items():
            if key == "adb_host" and "adb_port" in data:
                yield data["adb_host"], data["adb_port"]
                return

            if not isinstance(value, dict):
                continue

            if 'errcode' in value:
                continue
            else:
                yield value.get("adb_host"), value.get("adb_port")

    def push(self, src: str, path: str):
        """
            传输文件(push)
        :param src: 源文件
        :param path: 目标路径
        :return:
        """

        if not os.path.exists(src):
            raise FileNotFoundError(f"File not found: {src}")

        adb_path = self.utils.get_adb_path() or config.ADB_PATH
        if not os.path.exists(adb_path):
            raise FileNotFoundError(f"adb not found in {adb_path}")

        connect_list = list(self.__connect() or [])
        if not connect_list:
            raise RuntimeError("No available adb connections found")

        for (host, port) in connect_list:
            ret_code, retval = self.utils.run_command([adb_path, '-s', f"{host}:{port}", 'push', src, path],
                                                      mumu=False)

            if ret_code != 0:
                warnings.warn(retval)

        return True

    def push_download(self, src: str, new_name: str = None):
        """
            传输文件到Download文件夹(push)
        :param new_name:
        :param src: 源文件
        :param path: 目标路径
        :return:
        """
        if new_name:
            filename = new_name
        else:
            filename = os.path.basename(src)

        return self.push(src, f"/sdcard/Download/{filename}")

    def pull(self, src: str, path: str):
        """
            传输文件(pull)
        :param src: 源文件
        :param path: 目标路径
        :return:
        """

        adb_path = self.utils.get_adb_path() or config.ADB_PATH
        if not os.path.exists(adb_path):
            raise FileNotFoundError(f"adb not found in {adb_path}")

        connect_list = list(self.__connect() or [])
        if not connect_list:
            raise RuntimeError("No available adb connections found")

        for (host, port) in connect_list:
            ret_code, retval = self.utils.run_command([adb_path, '-s', f"{host}:{port}", 'pull', src, path],
                                                      mumu=False)

            if ret_code != 0:
                warnings.warn(retval)

        return True

    def clear(self, package: str):
        """
            清除应用数据(clear)
        :param package: 应用包名
        :return:
        """
        return self.__run_adb_cmd(f"shell pm clear {package}")
