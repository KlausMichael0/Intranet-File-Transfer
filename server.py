# -*- coding: utf-8 -*-
import Tkinter
import threading
import socket
import os


class ListenThread(threading.Thread):  # 监听线程

    def __init__(self, edit, server): #edit和server都是传递的参数
        threading.Thread.__init__(self)
        self.edit = edit  # 保存窗口中的多行文本框
        self.server = server

    def run(self):  # 进入监听状态
        while 1:  # 使用while循环等待连接
            try:  # 捕获异常
                client, addr = self.server.accept()  # 等待连接 接受TCP连接并返回（conn,address）,其中conn是新的套接字对象，可以用来接收和发送数据。address是连接客户端的地址。
                self.edit.insert(Tkinter.END, '连接来自:%s:%d\n' %
                                 addr)  # 向文本框输出状态
                data = client.recv(1024)  # 接收数据 接受TCP套接字的数据。数据以字符串形式返回，bufsize指定要接收的最大数据量  1024字节=1kb
                print('recieve filename = ' + data)
                self.edit.insert(Tkinter.END, '收到的文件:%s\n' % data)  # 向文本框中输出数据
                file = os.open(data, os.O_WRONLY | os.O_CREAT )  # 创建文件  打开收到的文件，读取其中的数据，创建新文件   只写/创建/判断是否已经存在此文件 | os.O_EXCL 
                while 1:
                    rdata = client.recv(1024)  # 接收数据
                    print('recieve data = ' + rdata)
		    os.write(file, rdata)  # 将数据写入文件
                    if not rdata:
                        break

                
                os.close(file)  # 关闭文件
                client.close()  # 关闭同客户端的连接
                self.edit.insert(Tkinter.END, '传送完毕\n')  # 向文本框中输出状态
            except IndexError, value:
                self.edit.insert(Tkinter.END, value)
                self.edit.insert(Tkinter.END, '关闭连接\n')
                break  # 结束循环


class Control(threading.Thread):  # 控制线程

    def __init__(self, edit):
        threading.Thread.__init__(self)
        self.edit = edit  # 保留窗口中的多行文本框
        self.event = threading.Event()  # 创建Event对象，用于多线程间通信
        self.event.clear()  # 清楚event标志  

    def run(self):
        server = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # 创建socket连接
        server.bind(('', 2333))  # 绑定本地端口2333
        server.listen(5)  # 开始监听
        self.edit.insert(Tkinter.END, '正在等待连接\n')  # 向文本框中输出状态
        
        
        self.lt = ListenThread(self.edit, server)  # 创建监听线程对象
        self.lt.setDaemon(True)  #将监听线程设置为守护进程  这时候，要是主线程A执行结束了，就不管子线程B是否完成,一并和主线程A退出.这就是setDaemon方法的含义
        self.lt.start()  # 执行监听线程
        self.event.wait()  # 进入等待状态
        server.close()  # 关闭连接

    def stop(self):  # 结束控制线程
        self.event.set()  # 设置event标志  进程会一直等待直到event对象的内部信号标志位为真。


class Window:  # 主窗口

    def __init__(self, root):
        self.root = root
        self.butlisten = Tkinter.Button(
            root, text='开始监听', command=self.listen)  # 创建组件
        self.butlisten.place(x=20, y=15)
        self.butclose = Tkinter.Button(root, text='停止监听', command=self.close)
        self.butclose.place(x=120, y=15)
        self.edit = Tkinter.Text(root)
        self.edit.place(y=50)

    def listen(self):  # 处理按钮事件
        self.ctrl = Control(self.edit)  # 创建控制线程对象
        self.ctrl.setDaemon(True)  #标记为守护进程，即使终端关闭之后也还会在后台运行。当主程序退出的时候，任何守护程序进程都会自动终止。
        self.ctrl.start()  # 执行控制线程

    def close(self):
        self.ctrl.stop()  # 结束控制线程


root = Tkinter.Tk()   #root是将Tk类实例化的结果，是一个实例。这会创建一个Tk的顶层小部件（就是创建一个小窗口），它通常是应用程序的主窗口
window = Window(root)
root.mainloop() #进入到事件循环，一旦检测到了事件，就刷新部件   就像连环画由多幅图组成   这个的作用就是去翻它！
