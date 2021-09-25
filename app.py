import json
import socket
import sys
import random
import string
import datetime
import time
import glob
import stat
import os
from pathlib import Path
from threading import Thread
from system_info import get_local_ip, get_drives_letters


class FileReceiver:

    def __init__(self):

        self.connections = {}
        self.drives = []
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
                self.list_of_paths.pop()
            
        elif len(path) > 0:
                self.list_of_paths.append(path)       
                    
        else:
            self.list_of_paths = []
            self.drives = get_drives_letters()
            return str(self.drives)

        files = glob.glob(self.list_of_paths[-1]+r"\\*")
        self.drives = []

        for f in files:
            if bool(os.stat(f).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) == False:
                self.drives.append(f)

        self.drives = [os.path.normpath(i) for i in self.drives]

        return str(self.drives)

    def accept_connections(self,local_address,port=4888):

        accept_connection_thread = Thread(target = self._accept_connections, args=(local_address,port,)) 
        accept_connection_thread.start()

    def _accept_connections(self,local_address,port):  

        self.receive_socket = socket.socket()
        self.receive_socket.bind((local_address,port))
        self.receive_socket.listen()

        while True:

            try:

                client_socket, addr = self.receive_socket.accept()
                string = client_socket.recv(port)

            except:
                break

            try:
            
                string = string.decode()
                send_back_socket = socket.socket()

                send_back_socket.connect((addr[0],port)) # zmienic pozniej na addr
                send_back_socket.send(str.encode("First mess"))

                
                self.new_thread = Thread(target = self.receive_data, args=(client_socket,send_back_socket,)) 
                self.new_thread.start()


            except Exception as e:
                print(e)
                continue



        self.receive_socket.close()


    def receive_data(self,client_socket,send_back_socket):

        while True:

            try:

                received = client_socket.recv(4096)
                received = received.decode()


                if received[:9] == "directory":

                    directory = self.get_directory(received[9:])
                    send_back_socket.send(str.encode(directory))


                elif received[:5] == "files":

                    list_paths = received[5:].split(';')

                    for p in list_paths:

                        total = 0

                        file_size = client_socket.recv(4096)
                        file_size = file_size.decode()
                        send_back_socket.send(str.encode("next"))

                        with open(p,"wb") as f:
                            while True:
                                if int(file_size) <= total: 
                                    break

                                recvfile = client_socket.recv(4096)
                                total = total + len(recvfile)


                                f.write(recvfile)

                            send_back_socket.send(str.encode("END"))

                elif received[:3] == "get":
                    file_paths = received[3:].split(';')

                    for f_path in file_paths:

                        if not os.path.isfile(f_path): 
                            send_back_socket.send(str.encode("NOT FOUND"))

                        else:

                            filesize = str(os.path.getsize(f_path))
                            
                            send_back_socket.send(str.encode(filesize))
                            client_socket.recv(4096)
                            
                        
                            with open(f_path,"rb") as f: 
                                sendfile = f.read(4096)
                                while sendfile:
                                    send_back_socket.send(sendfile)
                                    sendfile = f.read(4096)
                                print("Transfer finished")
                                client_socket.recv(4096)

                else:
                    send_back_socket.send(str.encode("test-test"))

            except Exception as e: 
                print(e)
                client_socket.close()
                send_back_socket.close()
                break


    def send_error(self):
            pass


class FileSender:

    def __init__(self):
        self.current_directiory = ""

    def connect(self,local_address,host_address,port=4888):

        print("Connecting to", host_address, port)

        try:
            self.s = socket.socket()
            self.s.connect((host_address,port))

            self.receive_socket = socket.socket()
            self.receive_socket.bind((local_address,port))
            self.receive_socket.listen()

        except:
            exit()

        self.s.send(str.encode("Establish connection"))
        
        self.sc, _ = self.receive_socket.accept()
        self.sc.recv(4096)


    def send_files(self,file_paths):
        self.new_thread = Thread(target = self._send_files, args=(file_paths,)) 
        self.new_thread.start()

    def _send_files(self,file_paths):

        file_paths_info = ""

        for f in file_paths:

            f = f.split("/")
            file_paths_info += f[-1] +  ";"

        else:

            file_paths_info = file_paths_info[:-1]

        self.s.send(str.encode("files"+str(file_paths_info)))

        for f_path in file_paths:


            filesize = str(os.path.getsize(f_path))
            
            self.s.send(str.encode(filesize))
            self.sc.recv(4096)

            with open(f_path,"rb") as f:

                sendfile = f.read(4096)

                while sendfile:
                    self.s.send(sendfile)
                    sendfile = f.read(4096)

                print("Finished sending")

                self.sc.recv(4096)

    def get_files(self,file_paths):
        self.new_thread = Thread(target = self._get_files, args=(file_paths,)) 
        self.new_thread.start()

    def _get_files(self,file_paths):

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
            received = self.sc.recv(4096)

            received = received.decode()

            print("received", received)
            if received != "NOT FOUND":

                file_size = received

                self.s.send(str.encode("next"))
                
                with open(f_path[-1],"wb") as f:

                    while True:

                        if int(file_size) <= total: 
                            break
                        recvfile = self.sc.recv(4096)
                        total = total + len(recvfile)
                        f.write(recvfile)

                    self.s.send(str.encode("END"))
           

    def get_directories(self,chosen_directory):

        try:

            to_send = "directory"+chosen_directory
            self.s.send(str.encode(to_send))

            while True:
                string = self.sc.recv(4096)
                break

        except Exception as e:
            return e
        
        return string   