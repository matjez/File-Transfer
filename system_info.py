import socket
import win32api, win32con
import os
import json

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    res = s.getsockname()[0]
    s.close()
    return res

def get_drives_letters():

    if os.name == "nt":

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

        return drives

def get_devices_list():
    with open("hosts.json") as hosts:
        try:
            host_file = json.loads(hosts.read())
            return host_file
        except:
            return []


def write_new_host(name,ip_address,port):
    hosts = get_devices_list()
    
    with open("hosts.json","w") as wrt_file:
        hosts["clients"][name] = [ip_address,port]
        json.dump(hosts, wrt_file, ensure_ascii=False, indent=4)
