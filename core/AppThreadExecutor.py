import sys
import threading
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget


class QTypeSignal(QObject):
    """
    信号对象, 用于线程间通信
    """
    # 定义一个信号
    send = pyqtSignal(object)

    def __init__(self):
        super(QTypeSignal, self).__init__()


class AppThreadExecutor:
    """
    耗时任务的封装，任务扔在线程池执行，执行完成后，通过信号通知主线程
    """

    def __init__(self):
        self.signal = QTypeSignal()
        self.pool = ThreadPoolExecutor()

    def _internal_callback(self, future):
        """
        线程池任务完成后，回调函数
        """
        print('_____internal_callback___', threading.currentThread().name)
        # 线程切换到主线程
        self.signal.send.emit(future)

    def submit(self, func, callback, *args, **kwargs):
        """
        @param func: 任务函数
        @param callback: 回调函数
        @param args: 任务函数参数
        """
        # 信号连接到回调函数
        self.signal.send.connect(callback)
        # 把任务提交到线程池
        future = self.pool.submit(func, *args, **kwargs)
        # 线程池任务完成后，回调函数
        future.add_done_callback(self._internal_callback)

    def shutdown(self, wait=True):
        """
        关闭线程池
        """
        self.pool.shutdown(wait)


def callback(future):
    """
    回调函数返回future对象，通过future.result()获取任务函数返回值
    """
    obj1, obj2 = future.result()
    print('_____callback___', threading.currentThread().name)
    print(obj1, obj2)


def task(param):
    """
    提交道线程池执行的任务
    """
    print(param, '_____task___', threading.currentThread().name)
    return 'hello', 'world'


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 300, 300)
        self.setWindowTitle('My Window')
        self.show()


if __name__ == '__main__':
    executor = AppThreadExecutor()
    executor.submit(task, callback, "hahaha")

    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
