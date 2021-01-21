import json
import socket
import sys

class FileTransfer:

    def __init__(self):
        self.host_list = self.get_devices_list()
        self.mode = "client" # host or client
        print(self.host_list)
     
    def get_devices_list(self):
        with open("hosts.json") as host_file:
            host_file = json.loads(host_file.read())
            return host_file

    def server_connection(self,address,hostname):
        s = socket.socket()
        s.bind(("192.168.8.123",4888))
        s.listen()

        while True:
            sc, address = s.accept()

            print(address)
            f = open('test.txt','wb') #open in binary
            while (True):       
            # receive data and write it to file
                l = sc.recv(1024)
                while (l):
                        f.write(l)
                        l = sc.recv(1024)
            f.close()

            sc.close()

        s.close()

    def client_connection(self,address,hostname):
        s = socket.socket()
        s.connect(("localhost",9999))
        f = open ("libroR.pdf", "rb")
        l = f.read(1024)
        while (l):
            s.send(l)
            l = f.read(1024)
        s.close()

    def add_host(self,address,hostname):
        pass

    def remove_host(self,address,hostname):
        pass

    def print_hosts(self):
        print(self.host_list)