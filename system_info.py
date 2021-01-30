import glob
import os

from pathlib import Path



sys = "windows"

def get_drives_letters():

    if sys == "windows":

        import win32api

        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]

        # i = 0
        # for drive in drives:
        #     drives[i] = drive[:-1] + "/"

        #     i+=1

        return drives


print(get_drives_letters())

directories = get_drives_letters()


print(os.listdir("C:\\"))