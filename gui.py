from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.core.window import Window
from kivy.lang import Builder
import kivy.properties as kyprops
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown 

from subprocess import Popen, PIPE
from threading import Thread

from app import *


# Builder.load_string("""

# <RemotePaths>:
#     spacing: 50
#     size_hint_y: 1
#     size_hint_x: 1
#     height: 100

#     ScrollView:
#         do_scroll_x: False
#         do_scroll_y: True
        
#         GridLayout:
#             orientation: "vertical"
#             size_hint_y: None
#             height: self.minimum_height
#             padding: 50, 50, 50, 50
# <Row>:
#     spacing: 50
#     size_hint_y: None
#     size_hint_x: 1
#     height: 100
# """)

class Directory(Button):
    def __init__(self, **kwargs):
        Button.__init__(self, **kwargs)
        self.register_event_type('on_double_press')

        if kwargs.get("on_double_press") is not None:
            self.bind(on_double_press=kwargs.get("on_double_press"))

    def on_touch_down(self, touch):
        if touch.is_double_tap and self.collide_point(touch.x, touch.y):
            self.dispatch('on_double_press', touch)
            return True
        return Button.on_touch_down(self, touch)
    def on_double_press(self, *args):

        pass


class MainFrame(GridLayout):

    def __init__(self, **kwargs):
        super(MainFrame, self).__init__(**kwargs)

        self.mode = "client"
        self.sender = None
        self.receiver = None

        self.drives = []
        self.drive_letter = ""
        self.current_path = ""

        self.files_to_download = set()

        self.cols = 2
        self.rows = 2

        self.left_up_grid_layout = GridLayout()
        self.left_up_grid_layout.cols = 2
        self.width = 1280
        self.height = 720

        self.left_up_grid_layout.size_hint = (None, None)
        self.left_up_grid_layout.height = 100
        self.left_up_grid_layout.width = Window.width * 0.25

        self.add_widget(self.left_up_grid_layout)

        self.left_up_grid_layout.add_widget(Button(text = "Refresh", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    pos_hint = (0, 0),
                    on_release = lambda a: self.refresh_list()
                ))  
        self.left_up_grid_layout.add_widget(Button(text = "Host/Client mode", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    on_release = lambda a: self.change_mode()
                ))  

        self.right_up_grid_layout = BoxLayout()
        self.right_up_grid_layout.size_hint = (1, None)
        self.right_up_grid_layout.height = 100
        self.add_widget(self.right_up_grid_layout)

        self.right_up_grid_layout.cols = 3
        self.right_up_grid_layout.add_widget(Button(text = "Directory", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, 1), 

                    width = 50,
                    on_release = lambda a: self.show_directiories()
                ))  
        self.right_up_grid_layout.add_widget(Button(text = "Add host", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, 1), 

                    width = 50,
                    on_release = lambda a: self.create_settings_frame()
                ))      
        self.right_up_grid_layout.add_widget(Button(text = "Create host", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, 1), 

                    width = 50,
                    on_release = lambda a: self.create_settings_frame()
                ))  
        self.right_up_grid_layout.add_widget(Button(text ="", 
                    color =(0, 0, 0, 1), 
                    background_normal = 'data/img/options_2.png', 
                    background_down ='data/img/options_2.png', 
                    size_hint = (1, 1), 

                    width = 50,
                    on_release = lambda a: self.create_settings_frame()
                ))  

        self.left_lower_box_layout = BoxLayout(orientation='vertical')
        self.left_lower_box_layout.size_hint = (None, 1)

        self.add_widget(self.left_lower_box_layout)
        self.left_lower_box_layout.cols = 3

        self.right_lower_grid_layout = GridLayout()
        
        self.right_lower_grid_layout.cols = 1
        self.right_lower_grid_layout.size_hint = (1, 1) # co to robi

        self.add_widget(self.right_lower_grid_layout)

        self.files_manage_bar = GridLayout(size_hint_y=None, height=100)
        self.files_manage_bar.cols = 2
        self.files_manage_bar.row = 1

        self.right_lower_grid_layout.add_widget(self.files_manage_bar)


        self.refresh_list()

        self.files_manage_bar.add_widget(Button(text = "Wyślij", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, None), 
                    on_release = lambda a: self.upload_files()
                ))  
        self.files_manage_bar.add_widget(Button(text = "Pobierz", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, None), 
                    on_release = lambda a: self.download_files()
                ))  

        self.content = GridLayout(size_hint_y=None)

        self.content.size_hint = (1,1)
        self.content.cols = 1

        self.right_lower_grid_layout.add_widget(self.content)


        
    def create_settings_frame(self):

        self.content.clear_widgets()
        self.content.add_widget(Label(text='Settings', color=(0,0,0,1)))     


    def create_remote_paths_frame(self,first_iteration=False):

        self.content.clear_widgets()
        self.scroll_view = ScrollView()


        self.content_scroll_view = GridLayout(size_hint_y=None, row_default_height=60, cols=1)
        self.content_scroll_view.bind(minimum_height=self.content_scroll_view.setter('height'))

        import ast
        paths = self.sender.get_directories(self.current_path).decode()

        print(paths, "parthsy tutaj")
        paths = ast.literal_eval(paths) 


        dropdown = DropDown() 

        if first_iteration == True:

            self.drives = paths
            current_drive = paths[0]
            self.current_path = current_drive

            paths = self.sender.get_directories(self.current_path).decode()
            paths = ast.literal_eval(paths) 
            
        
        else:
            current_drive = self.current_path.split("\\")[0]

        for drive in self.drives: 

            btn = Button(text = drive, size_hint_y = None, height = 40, on_press=self.change_drive) 

            btn.bind(on_release = lambda btn: dropdown.select(btn.text)) 

            dropdown.add_widget(btn) 

        
        print(current_drive)
        
        mainbutton = Button(text = current_drive, size_hint =(1, None), pos =(350, 300)) 

        mainbutton.bind(on_release = dropdown.open) 

        dropdown.bind(on_select = lambda instance, x: setattr(mainbutton, 'text', x)) 

        self.content.add_widget(mainbutton)

        

        for path in paths:

            path = path.split("\\")
        
            self.content_scroll_view.add_widget(Directory(text = path[-1], 
                    color =(0, 0, 0, 1), 
                    size_hint = (1, None), 
                    on_press = self.select_files,
                    on_double_press=self.change_path
                    
                ))  

        self.scroll_view.add_widget(self.content_scroll_view)

        self.content.add_widget(self.scroll_view)

        
        # self.content.add_widget(Label(text='test', color=(0,0,0,1)))  

    def change_drive(self, instance):
        print(instance.text, "trttete")
        self.current_path = ""
        self.change_path(instance.text)

    def change_path(self,*args,change_drive=False):

        print(type(args[0]))
        print(args[0])
        if type(args[0]) == str:
            

            if args[0] == "":
                self.current_path += args[0]
                self.create_remote_paths_frame(first_iteration=True)
            elif args[0] == "restore":
                self.create_remote_paths_frame(first_iteration=False)
            else:
                self.current_path += args[0]
                self.create_remote_paths_frame(first_iteration=False)
        else:
            print(args, args[0], args[0].text)    
            self.current_path += args[0].text + "\\"
            
            print(self.current_path, "tutaj")
            self.create_remote_paths_frame(self.current_path)

        self.files_to_download = set()

        print(self.current_path, "current paths tutaj jest")


    def select_files(self,instance):

        path = self.current_path + instance.text

        if path in self.files_to_download:            
            self.files_to_download.remove(path)
            instance.background_color = (1.0, 1.0, 1.0, 1.0)

        else:

            self.files_to_download.add(path)
            instance.background_color = (1.0, 0.0, 0.0, 1.0)


        print(self.files_to_download)

    
    def connection(self,instance):

        def get_address(list_of_devices):
            
            for name in list_of_devices:
                print(name)
                if name == instance.text:
                    res = list_of_devices[name]

                    return res

        

        if self.mode == "server":
            self.sender = None
            list_of_devices = get_devices_list()["server"]

            server_info = get_address(list_of_devices)
            print(server_info)

            self.receiver = FileReceiver()
            self.receiver.accept_connections(server_info[0],server_info[1])

        else:

            if self.sender == None: 
                
                self.receiver = None
                list_of_devices = get_devices_list()["client"]
                self.sender = FileSender()

                client_info = get_address(list_of_devices)
                print(client_info)

                self.sender.connect(client_info[0],client_info[1])
                self.change_path("")


    def connect_with_server(self,addr,port):
        if self.mode == "client":
            self.sender.connect(addr,port)

    def download_files(self):
        
        self.sender.get_files(self.files_to_download)

    def upload_files(self):

        pass

    def show_directiories(self):
        self.change_path("restore")

    def refresh_list(self):

        def add_list_of_widgets(devices):

            if len(devices) > 0: 
                for device in devices:
                    self.left_lower_box_layout.add_widget(Button(text = device, 
                            color = (0, 0, 0, 1), 
                            background_normal = '', 
                            size_hint = (1, 1), 
                            pos_hint = {"x":0.35, "y":0.3},
                            width = 50,
                            on_press = self.connection
                        ))  


        self.left_lower_box_layout.clear_widgets()
        list_of_devices = get_devices_list()

        if self.mode == 'client':
            
            add_list_of_widgets(list_of_devices["client"])

        else:

            add_list_of_widgets(list_of_devices["server"])

    def change_mode(self):

        if self.mode == 'server':
            self.mode = 'client'
        else:
            self.mode = 'server'
        
        self.refresh_list()

class GuiApp(App):

    def build(self):
        return MainFrame()

if __name__ == '__main__':

    Window.size = (1280, 720)
    Window.minimum_width, Window.minimum_height = Window.size
    Window.clearcolor = (1, 1, 1, 1)

    GuiApp().run()