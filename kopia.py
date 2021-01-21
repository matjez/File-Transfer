from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.core.window import Window
from subprocess import Popen, PIPE
from tinydb import TinyDB, Query

class FileTransfer:
    def __init__(self):
        self.hosts = TinyDB('hosts.json')
        self.host_list = {}

        for host in self.hosts:
            self.host_list = host
        
    def add_host(self):
        pass
    def print_hosts(self):
        print(self.host_list)

class LeftUpperGrid(GridLayout):
    def __init__(self, **kwargs):
        super(LeftUpperGrid, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Function 1', width=50, color=(0,0,0,1)))
        self.add_widget(Label(text='Function 2', width=50, color=(0,0,0,1)))


class RightUpperGrid(BoxLayout):
    def __init__(self,orientation='horizontal', **kwargs):
        super(RightUpperGrid, self,).__init__(**kwargs)
        self.cols = 3
        self.add_widget(Label(text='Function 1', width=50, color=(0,0,0,1)))
        self.add_widget(Label(text='Function 2', width=50, color=(0,0,0,1)))        
        self.add_widget(Label(text='Function 3', width=50, color=(0,0,0,1)))
        self.add_widget(Button(text ="", 
                     color =(1, 0, .65, 1), 
                     background_normal = 'data/img/options_2.png', 
                     background_down ='data/img/options_2.png', 
                     size_hint = (1, 1), 
                     pos_hint = {"x":0.35, "y":0.3},
                     width = 50,
                     on_release=  lambda a: self.transfer_app.host_list()
                   ))  
    def create_settings_window(self):
        print("tuta")
        self.process = Popen(['python', 'settings.py'], stdout=PIPE, stderr=PIPE)



class LeftLowerGrid(GridLayout):
    def __init__(self, **kwargs):
        super(LeftLowerGrid, self).__init__(**kwargs)
        self.cols = 3
        self.add_widget(Label(text='Function 1', color=(0,0,0,1)))



class RightLowerGrid(GridLayout):
    def __init__(self, **kwargs):
        super(RightLowerGrid, self).__init__(**kwargs)
        self.cols = 3
        self.add_widget(Label(text='Function 1', color=(0,0,0,1)))


class MainFrame(GridLayout):
    transfer_app = FileTransfer()
    def __init__(self, **kwargs):
        super(MainFrame, self).__init__(**kwargs)

        self.cols = 2
        self.rows = 2

        self.add_widget(LeftUpperGrid(width=250, size_hint_x=None))
        self.add_widget(RightUpperGrid(width=500, size_hint_x=None, orientation='horizontal'))
        self.add_widget(LeftLowerGrid(height = 400, width=250, size_hint_x=None))
        self.add_widget(RightLowerGrid(height = 400, width=500, size_hint_x=None))



class GuiApp(App):

    def build(self):
        return MainFrame()

if __name__ == '__main__':

    Config.set('graphics', 'width', '1000')
    Window.clearcolor = (1, 1, 1, 1)
    # Config.set('graphics', 'height', '200')
    GuiApp().run()