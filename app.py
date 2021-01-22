import json
import socket
import sys
import random
import string
import datetime


def key_generator():

    return "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=24))


class FileTransfer:

    def __init__(self):

        self.host_list = self.get_devices_list()
        self.mode = "client" # host or client

        self.connections = []

        print(self.host_list)

    def verify_connection_time(self):
        pass

    def accept_connections(self,address,hostname):

        receive_socket = socket.socket()
        receive_socket.bind(("192.168.8.162",4888))
        receive_socket.listen()

        while True:

            sc, addr = receive_socket.accept()
     
            l = sc.recv(1024)
            
            print(l)
            self.connections.append(l)

            send_back_socket = socket.socket()
            send_back_socket.connect(("192.168.8.123",4888))

            #key = key_generator()

            string_mess = "Connection accepted"
            send_back_socket.send(str.encode(string_mess))
            send_back_socket.close()

        receive_socket.close()

    def send_error(self):
        pass
     
    def get_devices_list(self):
        with open("hosts.json") as host_file:
            host_file = json.loads(host_file.read())
            return host_file

    def server_connection(self,address,hostname):
        s = socket.socket()
        s.bind(("192.168.8.123",4888))
        s.listen()

        while True:
            sc, addr = s.accept()

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

    def establish_connection(self,address,hostname):

        s = socket.socket()
        s.connect(("192.168.8.162",4888))

        key = key_generator()

        string_mess = "{}:{}:{}".format(hostname,address,key)

        s.send(str.encode(string_mess))

        receive_socket = socket.socket()
        receive_socket.bind(("192.168.8.123",4888))
        receive_socket.listen()

        while True:
            sc, addr = receive_socket.accept()

            back_message = sc.recv(1024)

            print(back_message)
            break

        s.close()
        receive_socket.close()

    def add_host(self,address,hostname):
        pass

    def remove_host(self,address,hostname):
        pass

    def print_hosts(self):
        print(self.host_list)

        

while True:

    print("1. Serwer")
    print("2. Połącz z serwerem")
    print("3. Wyślij pliki")

    transfer = FileTransfer()

    address = "192.168.8.1"
    hostname = "Komputer 1"

    x = input(": ")

    if(x == "1"):
        transfer.accept_connections(address,hostname)

    elif(x == "2"):
        transfer.establish_connection(address,hostname)

    elif(x == "3"):
        pass