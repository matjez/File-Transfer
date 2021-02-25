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

        return drives

def get_devices_list():
    with open("hosts.json") as host_file:
        host_file = json.loads(host_file.read())
        return host_file

class FileReceiver:

    def __init__(self):

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
            string = client_socket.recv(4096)

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
                received = client_socket.recv(4096)
                received = received.decode()

                print("asddsa")
                if received[:9] == "directory":

                    print("tetet",received)
                    directory = self.get_directory(received[9:])
                    print(directory)
                    send_back_socket.send(str.encode(directory))


                elif received[:5] == "files":

                    list_paths = received[5:].split(';')

                    print("CHUJJJ  ", list_paths)
                    print("CHUJJJ  ", received)

                    for p in list_paths:
                        print("tukej1")
                        total = 0

                        file_size = client_socket.recv(4096)
                        file_size = file_size.decode()
                        print("tukej2")
                        send_back_socket.send(str.encode("next"))

                        with open(p,"wb") as f:

                            while True:
                                #print("tutu")
                                print("Wielkosc pliku: ",file_size)
                                print("Total: ",total)

                                if int(file_size) <= total: 
                                    print("break")
                                    break
                                recvfile = client_socket.recv(4096)
                                total = total + len(recvfile)


                                f.write(recvfile)
                            print("koniec")
                            send_back_socket.send(str.encode("END"))

                elif received[:3] == "get":
                    file_paths = received[3:].split(';')

                    for f_path in file_paths:
                        filesize = str(os.path.getsize(f_path))
                        
                        send_back_socket.send(str.encode(filesize))
                        client_socket.recv(4096)
                        
                        # zrobic tak zeby najouerw wyslac wielkosc pliku
                        with open(f_path,"rb") as f:  # Zmienic pozniej na f path
                            sendfile = f.read(4096)
                            while sendfile:
                                send_back_socket.send(sendfile)
                                print('Sent ')
                                sendfile = f.read(4096)
                            print("DONE")
                            print(filesize)
                            client_socket.recv(4096)

                else:
                    send_back_socket.send(str.encode("test-test"))

            except Exception as e: 
                print("tutaj 2",e)
                client_socket.close()
                send_back_socket.close()
                break


    def send_error(self):
            pass
    

        

class FileSender:

    def __init__(self):
        self.current_directiory = ""

        
    def connect(self,addr,port=4888):

        print("Connecting to", addr, port)
        self.s = socket.socket()
        self.s.connect(("192.168.8.162",4888))


        self.receive_socket = socket.socket()
        self.receive_socket.bind(("192.168.8.123",4888))
        self.receive_socket.listen()

        self.s.send(str.encode("Establish connection"))
        
        self.sc, addr = self.receive_socket.accept()
        string = self.sc.recv(4096)
        print("Polaczonno", string)

    

    def send_files(self,file_paths):


        self.s.send(str.encode("files"+str(file_paths)))

        file_paths_splitted = file_paths.split(";")

        for f_path in file_paths_splitted:


            filesize = str(os.path.getsize(f_path))
            
            self.s.send(str.encode(filesize))
            self.sc.recv(4096)
            
            # zrobic tak zeby najouerw wyslac wielkosc pliku

            with open(f_path,"rb") as f:  # Zmienic pozniej na f path

                sendfile = f.read(4096)

                while sendfile:
                    self.s.send(sendfile)
                    print('Sent ')
                    sendfile = f.read(4096)

                print("DONE")
                print(filesize)
                self.sc.recv(4096)


    def get_files(self,file_paths):

        file_paths_info = ""
        for f in file_paths:
            file_paths_info += f +  ";"
        else:
            file_paths_info = file_paths_info[:-1]

        self.s.send(str.encode("get"+str(file_paths_info)))

        file_paths = list(file_paths)

        for f_path in file_paths:

            f_path = f_path.split("\\")
            total = 0
            file_size = self.sc.recv(4096)
            file_size = file_size.decode()
            print("tukej2")
            self.s.send(str.encode("next"))
            
            with open(f_path[-1],"wb") as f:
                while True:
                    #print("tutu")
                    print("Wielkosc pliku: ",file_size)
                    print("Total: ",total)
                    if int(file_size) <= total: 
                        print("break")
                        break
                    recvfile = self.sc.recv(4096)
                    total = total + len(recvfile)
                    f.write(recvfile)
                print("koniec")
                self.s.send(str.encode("END"))
           

    def get_directories(self,chosen_directory):

        # zrobic zeby mozna bylo dluzsze robic xD

        try:
            print("test")
            to_send = "directory"+chosen_directory
            print(to_send)
            print(to_send)
            print(to_send)
            self.s.send(str.encode(to_send))


            while True:
                string = self.sc.recv(4096)
                print(string.decode())
                break

        except Exception as e:
            # self.s.close()
            # self.receive_socket.close()
            print(e)
            return e
        
        return string   

    def add_host(self,address,hostname):
        pass

    def remove_host(self,address,hostname):
        pass
"""
while True:

    print("1. Serwer")
    print("2. Połącz z serwerem")


    receive = FileTransfer.FileReceiver()

    address = "192.168.8.1"
    hostname = "Komputer 1"

    file_paths = "xtest1.txt;xtest2.txt;xtest3.txt"

    x = input(": ")

    if(x == "1"):
        receive.accept_connections(address,hostname)

    elif(x == "2"):

        send = FileTransfer.FileSender()
        send.connect("192.168.8.162")
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

            elif(x == "3"):
                x = input()
                send.get_files(file_paths)
                
"""