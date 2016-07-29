#!/usr/bin/env python
# -*-coding=utf-8-*-
# Auther:ccorz Mail:ccniubi@163.com Blog:http://www.cnblogs.com/ccorz/
# GitHub:https://github.com/ccorzorz

import pika, subprocess, socket, os

# 获取本地IP地址
ip = socket.gethostbyname(socket.gethostname())
# 获取当前用户的家目录
dir = os.path.expanduser('~')

#创建连接对象,绑定RabbitMQ服务器IP,
connection = pika.BlockingConnection(pika.ConnectionParameters(host='192.168.4.193'))
#创建频道
channel = connection.channel()
# channel.queue_declare(queue='RPC')
#订阅模式,随机创建列队
channel.exchange_declare(exchange='RPC',type='fanout')
result=channel.queue_declare(exclusive=True)
queue_name=result.method.queue
#绑定相关消息队列
channel.queue_bind(exchange='RPC',queue=queue_name)

#接受到命令后,运行处理结果
def cmd_handle(body):
    obj = subprocess.Popen(body, shell=True,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           universal_newlines=True)
    res = obj.stdout.read()
    res_err = obj.stderr.read()
    obj.stdout.close()
    obj.stderr.close()
    if res_err:
        return '%s\n============\n%s' % (ip, res_err)
    else:

        return '%s\n============\n命令执行成功!\n%s' % (ip, res)

#回调函数
def callback(ch, method, properties, body):
    print('Recive cmd:%s' % body)
    #处理命令,并返回结果
    response = cmd_handle(body)
    #将结果返回给server端
    ch.basic_publish(exchange='',
                     routing_key=properties.reply_to,
                     # properties=pika.BasicProperties(
                     #     correlation_id=properties.correlation_id
                     # ),
                     body=response,
                     )
    #durable 消息不丢失
    ch.basic_ack(delivery_tag=method.delivery_tag)

#改变默认获取消息顺序,谁来谁取
channel.basic_qos(prefetch_count=1)
#阻塞状态,接受远程命令
channel.basic_consume(callback, queue=queue_name)
channel.start_consuming()
