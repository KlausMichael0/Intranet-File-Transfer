---
title: 内网文件传输
date: 2019-05-07 08:31:26
tags: Inner-File-Trans
---

设计并实现一个局域网内部的文件传送工具，使用TCP协议进行可靠文字传输。

<!-- more -->
### 服务器端

#### 最终

```python
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
                file = os.open(data, os.O_WRONLY | os.O_CREAT | os.O_EXCL )  # 创建文件  打开收到的文件，读取其中的数据，创建新文件   只写/创建/判断是否已经存在此文件
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
```



服务器端整体设计流程：

1. 创建顶层小部件
2. 定义`Window`类
   - 重写`__init__`方法
     - 创建组件
       - 开始监听，按下此组件将会调用`listen()`方法
       - 停止监听，按下此组件将会调用`close()`方法
   - 定义`listen()`方法
     - 创建控制线程对象
     - 将控制线程对象标记为守护进程，当主程序退出时，任何守护进程都会自动终止。
     - 执行控制线程
       - 重定义初始化函数，传入文本框，创建event对象，便于多线程通信
       - 重写run方法，创建基于TCP的socket连接，创建**监听进程对象**，执行监听进程并等待
       - **监听进程**
         - 重定义初始化函数，重写run方法，写入传输的文件数据
       - 结束控制进程方法
   - 定义`close()`方法
     - 调用结束控制线程方法
3. 定义`Control`类
   - 重写`__init__`方法
     - 创建线程，载入文本框
     - 创建Event对象，Event对象实现了简单的线程通信机制，它提供了设置信号、清除信号、等待等，如果信号标志位为假，则其他线程必须等待某个事件的发生，只有规定的事件发生并将标志位置为真时，其他线程才会被激活。
     - 清除Event对象的标志位（置为假）
   - 定义`run()`方法
     - 创建基于TCP的socket连接，绑定本地端口2333，开始监听
     - 创建监听进程，执行监听进程并等待
   - 定义`stop()`方法
     - 将Event的信号位置为真，即可结束控制进程。
4. 定义`ListenThread`类
   - 重写`__init__`方法
     - 传入多行文本框和socket连接
   - 重写`run()`方法
     - 进入监听状态。输出收到的文件的文件名
     - 判断是否已经存在同名文件，若不存在则创建新的文件
     - 接受文件中的数据，写入新文件中
     - 写入完成以后断开连接
5. 进入事件循环，使用`mainloop()`

​    

### 客户端

#### 最终

```python
# -*- coding: utf-8 -*-
import Tkinter
import tkFileDialog
import socket
import os
import time


class Window:

    def __init__(self, root):  # 创建组件
        label1 = Tkinter.Label(root, text='IP')
        label2 = Tkinter.Label(root, text='Port')
        label3 = Tkinter.Label(root, text='文件')
        label1.place(x=5, y=5)
        label2.place(x=5, y=30)
        label3.place(x=5, y=55)

        self.entryIP = Tkinter.Entry(root)
        self.entryIP.insert(Tkinter.END, '127.0.0.1')
        self.entryPort = Tkinter.Entry(root)
        self.entryPort.insert(Tkinter.END, '2333')
        self.entryData = Tkinter.Entry(root)
        self.entryData.insert(Tkinter.END, 'Hello')

        self.Recv = Tkinter.Text(root)
        self.entryIP.place(x=40, y=5)
        self.entryPort.place(x=40, y=30)
        self.entryData.place(x=40, y=55)

        self.Recv.place(y=105)
        self.send = Tkinter.Button(root, text='发送数据', command=self.send)
        self.openfile = Tkinter.Button(root, text='浏览', command=self.open_file)
        self.send.place(x=40, y=80)
        self.openfile.place(x=170, y=55)

    def send(self):  # 按钮事件
        try:  # 异常处理
            ip = self.entryIP.get()  # 获取IP
            port = self.entryPort.get()  # 获取端口
            filename = self.entryData.get()  # 获取发送数据
            tt = filename.split('/')
            name = tt[len(tt) - 1]
            client = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)  # 创建socket对象

            client.connect((ip, int(port)))  # 连接服务器
            print('filename: ' + name)
            client.send(name)  # 发送数据

            time.sleep(3)

            file = os.open(filename, os.O_RDONLY |
                           os.O_EXCL)  # 打开文件
            while 1:  # 发送文件
                data = os.read(file, 1024)
                if not data:
                    break
                print('filename data : ' + data)
                client.send(data)
            os.close(file)
            client.close()  # 关闭连接
        except IndexError, value:
            print(value)
            self.Recv.insert(Tkinter.END, '发送错误\n')

    def open_file(self):
        r = tkFileDialog.askopenfilename(
            title='Python Tkinter',
            filetypes=[('All Files', '*'), ('Python', '*.py *.pyw')])
        if r:
            self.entryData.delete(0, Tkinter.END)
            self.entryData.insert(Tkinter.END, r)


root = Tkinter.Tk()
window = Window(root)
root.mainloop()
```



客户端整体设计流程：

1. 创建顶层小部件
2. 定义`Window`类
   - 重写`__init__`方法
     - 创建多个组件和文本输入框。
   - 重写`open_file`方法
     - `askopenfilename`创建了一个文件会话对象，简而言之就是跳出选择文件框。
     - 如果文件存在，则将文件名（包括路径）写入到`文件`后的Text框中。
   - 定义`send`按钮事件
     - 从三个Text框中获取数据，建立socket连接。
     - 发送文件名，发送文件中的数据（数据流，返回的是一个一个的字符串）。

​    




