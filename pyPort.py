import socket
import threading


class Client(threading.Thread):
    def __init__(self,ip):
        threading.Thread.__init__(self)
        # 创建一个socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 主动去连接局域网内IP为192.168.27.238，端口为6688的进程
        self.client.connect((ip, 10086))

    def run(self):

        while True:
            # 接受控制台的输入
            _ = self.client.recv(1024)
            print("recv:",_)
            # 对数据进行编码格式转换，不然报错

            # 如果输入quit则退出连接

            #self.client.sendall(data)

        # 发送数据告诉服务器退出连接

    def quit(self):
        self.client.close()

if __name__ == '__main__':
    c = Client('127.0.0.1')
    c.start()