import json
import socket
import sys
import random
import string
import datetime
import time
from glob import glob

from threading import Thread


class FileReceiver:

    def __init__(self):

        self.host_list = self.get_devices_list()

        self.connections = {}
        self.current_directiory = ""

    def key_generator(self):

        while True:

            switch = False
            key = "".join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=24))

            if len(self.connections.keys()) > 0:
                for connection in self.connections.keys():
                    if self.connections[connection][0] == key:
                        switch = True
                        break

                if switch != True:
                    return key

            else:
                return key


    def verify_connection_time(self):

        time.sleep(15)

        now = datetime.datetime.now()
        
        for connection in self.connections.keys():
            diff = now - self.connections[connection][1]
            if (diff.total_seconds() / 60) > 30:
                self.connections[connection][0].close()
                del self.connections[connection]
    
    def get_directory(self):

        return glob('C:\\')

    def accept_connections(self,address,hostname):

        receive_socket = socket.socket()
        receive_socket.bind(("192.168.8.162",4888))
        receive_socket.listen()

        while True:
            
        
            client_socket, addr = receive_socket.accept()
            string = client_socket.recv(1024)

            try:
            
                string = string.decode()


                #new_key = self.key_generator()
                #self.connections[new_key] = [new_socket,datetime.datetime.now(), addr]

                send_back_socket = socket.socket()

                send_back_socket.connect(("192.168.8.123",4888)) # zmienic pozniej na addr
                send_back_socket.send(str.encode("Pierwsza wiadomosc"))

                
                new_thread = Thread(target = self.receive_data, args=(client_socket,send_back_socket,)) 
                new_thread.start()
                


            except Exception as e:
                print("tutaj 1",e)
                continue



        receive_socket.close()


    def receive_data(self,client_socket,send_back_socket):

        print("1111")
        while True:
            try:
                print("2222")
                received = client_socket.recv(1024)
                received = received.decode()
                print("asddsa")
                if received == "directory":
                    print("wyslano sciezke")
                    directory = str(self.get_directory())
                    send_back_socket.send(str.encode(directory))
                else:
                    send_back_socket.send(str.encode("test-test"))

            except Exception as e:
                print("tutaj 2",e)
                client_socket.close()
                send_back_socket.close()
                break


    def send_error(self):
        pass
     
    def get_devices_list(self):
        with open("hosts.json") as host_file:
            host_file = json.loads(host_file.read())
            return host_file
        

class FileSender:

    def __init__(self):

        self.host_list = self.get_devices_list()

        self.current_directiory = ""

        self.s = socket.socket()
        self.s.connect(("192.168.8.162",4888))


        self.receive_socket = socket.socket()
        self.receive_socket.bind(("192.168.8.123",4888))
        self.receive_socket.listen()

        self.s.send(str.encode("Establish connection"))
        
        self.sc, addr = self.receive_socket.accept()
        string = self.sc.recv(1024)
        print(string)
        print(self.get_directories(" "))

     
    def get_devices_list(self):
        with open("hosts.json") as host_file:
            host_file = json.loads(host_file.read())
            return host_file

    def send_files(self):



        try:
            self.s.send(str.encode(x))

            while True:
                print("tototot")

                string = self.sc.recv(1024)
                print(string)
                break
        except Exception as e:
            self.s.close()
            self.receive_socket.close()
            print(e)
            

    def get_directories(self,chocen_directory):

        # zrobic zeby mozna bylo dluzsze robic xD

        try:
            self.s.send(str.encode("directory"))


            while True:
                string = self.sc.recv(1024)
                print(string)
                break

        except Exception as e:
            self.s.close()
            self.receive_socket.close()
            return e
        
        return string
    """
    def establish_connection(self,address,hostname):

        self.s = socket.socket()
        self.s.connect(("192.168.8.162",4888))


        self.receive_socket = socket.socket()
        self.receive_socket.bind(("192.168.8.123",4888))
        self.receive_socket.listen()

        self.s.send(str.encode("Establish connection"))
        
        self.sc, addr = self.receive_socket.accept()
        string = self.sc.recv(1024)
        print(string)
        print(self.get_directories(" "))

        
        #string_mess = "{}:{}:{}".format(hostname,"","None")
       """     

    def add_host(self,address,hostname):
        pass

    def remove_host(self,address,hostname):
        pass

    def print_hosts(self):
        print(self.host_list)

        

while True:

    print("1. Serwer")
    print("2. Połącz z serwerem")



    
    receive = FileReceiver()

    address = "192.168.8.1"
    hostname = "Komputer 1"

    x = input(": ")

    if(x == "1"):
        receive.accept_connections(address,hostname)

    elif(x == "2"):

        send = FileSender()

        while True:

            print(" ")
            print("1. Ścieżka plików")
            print("2. Wyślij pliki")
            
            x = input("Wybierz: ")

            
            if(x == "1"):
                print("")
                print(send.current_directiory)
                x = input("path: ")
                send.get_directories(x)
            
            elif(x == "2"):
                x = input()
                send.send_files()
            