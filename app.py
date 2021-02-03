import json
import socket
import sys
import os
import random
import string
import datetime
import time
import glob

from threading import Thread

import stat
import win32api, win32con
from pathlib import Path


def get_drives_letters():

    if os.name == "nt":

        

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

        # i = 0
        # for drive in drives:
        #     drives[i] = drive[:-1] + "/"

        #     i+=1
    

        return drives


class FileReceiver:

    def __init__(self):

        self.host_list = self.get_devices_list()

        self.connections = {}
        self.current_directiory = ""
        self.directories = []
        self.list_of_paths = []

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
    
    def get_directory(self,path):

        if path == "back" and len(self.list_of_paths) > 1:
                print("jeden")
                self.list_of_paths.pop()
            
        elif len(path) > 0:
                print("dwa")
                self.list_of_paths.append(path)       
                     
        else:
            print("trzy")
            self.list_of_paths = []
            self.directories = get_drives_letters()
            return str(self.directories)

        print(self.list_of_paths)

        files = glob.glob(self.list_of_paths[-1]+r"\\*")
        self.directories = []

        for f in files:
            if bool(os.stat(f).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) == False:
                self.directories.append(f)

        self.directories = [os.path.normpath(i) for i in self.directories]

        return str(self.directories)

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
                if received[:9] == "directory":

                    print("tetet",received)
                    directory = self.get_directory(received[9:])
                    send_back_socket.send(str.encode(directory))

                    
                elif received[:5] == "files":

                    list_paths = list(received[5:])

                    for p in list_paths:

                        total = 0
                        file_size = client_socket.recv(1024)
                        file_size = file_size.decode()

                        send_back_socket.send(str.encode("next"))

                        with open(p,"wb") as f:

                            while True:
                                print("tutu")
                                recvfile = client_socket.recv(1024)

                                print(recvfile)
                                if file_size == total: 
                                    print("break")
                                    break
                                total = total + len(recvfile)


                                f.write(recvfile)
                            print("koniec")

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

    def send_files(self,file_paths):


        self.s.send(str.encode("files"+str(file_paths)))

        for f_path in file_paths:

            filesize = str(os.path.getsize(f_path))
            self.s.send(str.encode(filesize))
            self.sc.recv(1024)
                                             # zrobic tak zeby najouerw wyslac wielkosc pliku

            with open("F:\\test.txt","rb") as f:  # Zmienic pozniej na f path

                sendfile = f.read(1024)
                while sendfile:
                    self.s.send(sendfile)
                    print('Sent ')
                    sendfile = f.read(1024)
                
                self.s.send(b"DONE")

                print("DONE")
                    


            
    """                
    def send_files(self,file_paths):


        for _ in len(files_paths):
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
    """                

    def get_directories(self,chosen_directory):

        # zrobic zeby mozna bylo dluzsze robic xD

        try:
            to_send = "directory"+chosen_directory
            print(to_send)
            print(to_send)
            print(to_send)
            self.s.send(str.encode(to_send))


            while True:
                string = self.sc.recv(1024)
                print(string.decode())
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

    file_paths = ["xtest1.txt","xtest2.txt","xtest3.txt"]

    x = input(": ")

    if(x == "1"):
        receive.accept_connections(address,hostname)

    elif(x == "2"):

        send = FileSender()
        send.get_directories("")
        
        while True:

            print(" ")
            print("1. Ścieżka plików")
            print("2. Wyślij pliki")
            print("3. Pobierz pliki")

            x = input("Wybierz: ")

            if(x == "1"):
                print("")
                path = input("path: ")
                print(x)
                send.get_directories(path)

            elif(x == "2"):
                x = input()
                send.send_files(file_paths)
            