import datetime
import time

import pandas as pd

"""
时间操作工具
参考链接： https://www.jianshu.com/p/cdd6c5874892
"""


def str_to_stamp(time_str, format_str):
    """
    字符串转时间戳
    :param time_str: 时间字符串 eg: '2022-10-25 22:20:10'
    :param format_str: 格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :return:
    """
    time_array = time.strptime(time_str, format_str)
    time_stamp = int(time.mktime(time_array))
    return time_stamp


def stamp_to_str(timestamp, format_str):
    """
    时间戳转格式化时间字符串
    :param timestamp: 时间戳 eg: 1660060800
    :param format_str: 格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :return:
    """
    time_array = time.localtime(int(timestamp))
    return time.strftime(format_str, time_array)


def time_str_delta(time_str, format_str, **offset):
    """
    格式化时间偏移
    :param time_str: 时间字符串 eg: '2022-10-25 22:20:10'
    :param format_str: 格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :param offset: 偏移单位 eg: days=3 或 weeks=3
    :return: 偏移后的时间字符串
    """
    if len(offset) > 1:
        raise Exception('字典size不能大于1，参考eg')

    # 任意时间字符串转为datetime
    time_instance = datetime.datetime.strptime(time_str, format_str)
    key = ''
    value = 0
    for key, value in offset.items():
        key = str(key)
        value = int(value)
    offset_time = None
    if key == 'days':
        offset_time = time_instance + datetime.timedelta(days=value)
    if key == 'weeks':
        offset_time = time_instance + datetime.timedelta(weeks=value)
    if key == 'hours':
        offset_time = time_instance + datetime.timedelta(hours=value)
    if key == 'minutes':
        offset_time = time_instance + datetime.timedelta(minutes=value)
    if key == 'milliseconds':
        offset_time = time_instance + datetime.timedelta(milliseconds=value)
    return datetime.datetime.strftime(offset_time, format_str)


def timestamp_delta_to_str(timestamp, format_str, **offset):
    """
    时间戳时间偏移
    :param timestamp: 时间戳 1660060800
    :param format_str: 格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :param offset: 偏移单位 eg: days=3 或 weeks=3
    :return: 偏移后的时间字符串
    """
    # timestamp转为datetime
    time_instance = datetime.datetime.fromtimestamp(timestamp)
    key = ''
    value = 0
    for key, value in offset.items():
        key = str(key)
        value = int(value)
    offset_time = None
    if key == 'days':
        offset_time = time_instance + datetime.timedelta(days=value)
    if key == 'weeks':
        offset_time = time_instance + datetime.timedelta(weeks=value)
    if key == 'hours':
        offset_time = time_instance + datetime.timedelta(hours=value)
    if key == 'minutes':
        offset_time = time_instance + datetime.timedelta(minutes=value)
    if key == 'milliseconds':
        offset_time = time_instance + datetime.timedelta(milliseconds=value)
    return datetime.datetime.strftime(offset_time, format_str)


def is_today_str(time_str, format_str):
    """
    是否时今天
    :param time_str: 时间字符串 eg: '2022-10-25 22:20:10'
    :param format_str:格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :return: 是否是今天
    """
    today_instance = datetime.datetime.now()
    time_instance = datetime.datetime.strptime(time_str, format_str)

    today_str = datetime.datetime.strftime(today_instance, '%Y%m%d')
    tmp_time_str = datetime.datetime.strftime(time_instance, '%Y%m%d')
    return tmp_time_str == today_str


def is_today_timestamp(timestamp):
    """
    是否时今天
    :param time_str: 时间字符串 eg: '2022-10-25 22:20:10'
    :param format_str:格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :return: 是否是今天
    """
    today_instance = datetime.datetime.now()
    time_instance = datetime.datetime.fromtimestamp(timestamp)

    today_str = datetime.datetime.strftime(today_instance, '%Y%m%d')
    tmp_time_str = datetime.datetime.strftime(time_instance, '%Y%m%d')
    return tmp_time_str == today_str


def format_convert(time_str, src_format_str, dst_format_str):
    """
    时间字符串格式转换
    :param time_str: 时间字符串 eg: '2022-10-25 22:20:10'
    :param src_format_str: 格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :param dst_format_str: 格式化字符串 eg: '%Y-%m-%d %H:%M:%S'
    :return:
    """
    time_instance = datetime.datetime.strptime(time_str, src_format_str)
    return datetime.datetime.strftime(time_instance, dst_format_str)


def timestamp_to_str(time_stamp: pd.Timestamp, format_str='%Y-%m-%d') -> str:
    """
    Timestamp 数据类型格式化为字符串，
    主要是用来处理数据库查出来的日期 index
    """
    return str(pd.to_datetime(time_stamp, format=format_str).date())


def cur_millis():
    """
    当前的毫秒数
    :return:
    """
    return int(round(time.time() * 1000))


if __name__ == '__main__':
    str_time = '20220810'
    format = '%Y%m%d'

    timestamp = str_to_stamp(str_time, format)
    str_time_format = stamp_to_str(timestamp, format)
    print(timestamp)
    print(str_time_format)

    str_delta1 = time_str_delta(str_time, format, weeks=3)
    str_delta2 = time_str_delta(str_time, format, weeks=-3)
    print(f'字符串格式日偏移：正向偏移{str_delta1} 反向偏移{str_delta2}')

    str_delta3 = timestamp_delta_to_str(timestamp, format, days=5)
    str_delta4 = timestamp_delta_to_str(timestamp, format, days=-5)
    print(f'时间戳日偏移：正向偏移{str_delta3} 反向偏移{str_delta4}')

    print(is_today_str('20221120', format))
    print(is_today_str('20221121', format))
