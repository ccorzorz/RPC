#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz

import pika

class Center:
    def __init__(self):
        """
        构造方法,初始化数据
        :return:
        """
        #创建对象,绑定IP
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='192.168.4.193'))
        self.channel = self.connection.channel()
        #设定消息队列获取模式为订阅
        self.channel.exchange_declare(exchange='RPC', type='fanout')
        #定义接受返回消息的队列
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.relay_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    def relay_response(self, ch, method, props, body):
        """
        定义返回消息后的处理方法
        :param ch:
        :param method:
        :param props:
        :param body:
        :return:
        """
        self.response = body

    def request(self, cmd):
        """
        定义发送远程命令的方法
        :param cmd: 命令
        :return:
        """
        self.response = None
        #发送命令请求,并在属性中设定返回队列
        self.channel.publish(exchange='RPC',
                             routing_key='',
                             properties=pika.BasicProperties(
                                 reply_to=self.callback_queue,
                             ),
                             body=str(cmd))
        #接受返回的消息
        while self.response is None:
            self.connection.process_data_events()
        #打印消息
        print(str(self.response,encoding='utf8'))

#主函数
def main():
    #循环
    while True:
        #创建对象
        center = Center()
        #输入命令
        cmd = input('请输入操作命令,输入"q"退出:')
        if cmd == 'q':
            print('系统退出!')
            return
        else:
            #执行方法,发送命令并接受返回结果
            center.request(cmd)


if __name__ == '__main__':
    main()
