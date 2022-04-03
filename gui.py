from re import A
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.dropdown import DropDown 
from threading import Thread
from tkinter import filedialog, Tk
from app import FileReceiver, FileSender

from system_info import get_devices_list, get_local_ip, write_new_host
import ast

class FileUploadDialog(Thread):

    def __init__(self):
        Thread.__init__(self)

    def return_file_paths(self):

        self.root = Tk()
        self.root.withdraw()

        file_paths = filedialog.askopenfilenames()
        return file_paths

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

class ContentFrame(BoxLayout):

    def __init__(self, content_type, **kwargs):
        BoxLayout.__init__(self, **kwargs)

        self.orientation = 'vertical'
        self.spacing = 25
        self.padding = (50, 50, 150, 100)
        self.input_fields = []
        self.last_string = ["","",""]

        if content_type == "Add host":
            self.host_addition()

        elif content_type == "Settings":
            self.settings()

        else:
            pass

    def host_addition(self):

        def add_grid(widget_1, widget_2):
            grid = GridLayout()
            grid.cols = 2
            grid.add_widget(widget_1)
            grid.add_widget(widget_2)
            self.add_widget(grid),

        def validate(instance, value):

            def block_previous(num):
                last_str_len = len(self.last_string[num])
                text_len = len(instance.text)

                if last_str_len != 0:
                    if text_len == 1:
                        self.last_string[num] = ""
                        instance.text == ""

                    else:
                        for i in range(0,last_str_len):
                            if last_str_len > text_len:
                                self.last_string[num] = instance.text
                                return True

                            elif instance.text[i] != self.last_string[num][i]:
                                instance.text = self.last_string[num]
                        
                else:
                    return False

            if len(value) > 0:
                char = value[-1]

                if instance.id == "name_text":
                    if block_previous(0):
                        return

                    if char.isalpha() or char.isdigit() or char in ("_"," "):
                        if len(value) > 20:
                            instance.text = instance.text[:-1]
                        else:
                            self.last_string[0] = instance.text
                
                    else:
                        instance.text = instance.text[:-1]

                elif instance.id == "ip_address_text":
                    if block_previous(1):
                        return

                    if char.isdigit() or char == ".":
                        if len(value) > 15:
                            instance.text = instance.text[:-1]

                        elif char == "." and instance.text[-2] == ".":
                            instance.text = instance.text[:-1]

                        else:

                            dig_counter = 0
                            dot_counter = 0

                            for c in instance.text[::-1]: # loop reversed value
                                if c.isdigit():
                                    dig_counter += 1

                                elif c == ".":
                                    dig_counter = 0
                                    dot_counter +=1

                                if dig_counter > 3 or dot_counter > 3:
                                    instance.text = instance.text[:-1]
                                    break
                                else:
                                    self.last_string[1] = instance.text

                    else:
                        instance.text = instance.text[:-1]

                elif instance.id == "port_text":
                    if block_previous(2):
                        return

                    if char.isdigit():
                        if len(value) > 5:
                            instance.text = instance.text[:-1]
                        else:
                            self.last_string[2] = instance.text

                    else:
                        instance.text = instance.text[:-1]

            
        grid = GridLayout()
        grid.cols = 2

        name_text = TextInput(id="name_text",focus_previous=True)
        name_text.halign = "center"
        name_text.valign = "middler"
        name_text.size_hint_y = 0.5
        name_text.font_size = name_text.height * 0.3
        name_text.bind(text=validate)

        self.input_fields.append(name_text)
        add_grid(Label(text="Name", color=(0,0,0,1), font_size='25sp'),name_text)

        ip_address_text = TextInput(id="ip_address_text")
        ip_address_text.halign = "center"
        ip_address_text.valign = "middler"
        ip_address_text.size_hint_y = 0.5
        ip_address_text.font_size = name_text.height * 0.3
        ip_address_text.bind(text=validate)

        self.input_fields.append(ip_address_text)
        add_grid(Label(text="Ip address", color=(0,0,0,1), font_size='25sp'),ip_address_text)

        port_text = TextInput(id="port_text")
        port_text.halign = "center"
        port_text.valign = "middler"
        port_text.size_hint_y = 0.5
        port_text.font_size = name_text.height * 0.3
        port_text.bind(text=validate)

        self.input_fields.append(port_text)
        add_grid(Label(text="Port", color=(0,0,0,1), font_size='25sp'),port_text)
        add_grid(Label(text=""),Button(text="Add", color=(0,0,0,1), font_size='25sp', on_release= lambda a: self.on_button_click()))

    def on_button_click(self):

        if len(self.input_fields[0].text) == 0:
            return False

        elif len(self.input_fields[1].text) == 0:
            return False

        elif len(self.input_fields[2].text) == 0:
            return False

        else:
            write_new_host(self.input_fields[0].text,
                            self.input_fields[1].text,
                            int(self.input_fields[2].text))

    def settings(self):

        settings_grid = GridLayout()
        settings_grid.rows = 8
        settings_grid.size_hint = (1,1)

        settings_grid.add_widget(Label(text="Clear hosts list.", color=(0,0,0,1), size_hint=(None,1)))
        settings_grid.add_widget(Button(text="Clear", color=(0,0,0,1), size_hint=(None,None),height=10, on_release= lambda a: self.on_button_click()))
        settings_grid.add_widget(Label(text="This is place for future settings", color=(0,0,0,1)))
        settings_grid.add_widget(Label(text="This is place for future settings", color=(0,0,0,1)))
        settings_grid.add_widget(Label(text="This is place for future settings", color=(0,0,0,1)))
        
        self.add_widget(settings_grid)

class MainFrame(GridLayout):

    def __init__(self, **kwargs):
        super(MainFrame, self).__init__(**kwargs)

        self.mode = "client"
        self.sender = None
        self.receiver = None

        self.drives = []
        self.drive_letter = ""
        self.current_path = ""

        self.ip_address = get_local_ip()

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
                    color =(1, 1, 1, 1), 
                    background_normal = '', 
                    background_color = (0,0.2,0.65,0.9), 
                    pos_hint = (0, 0),
                    on_release = lambda a: self.refresh_list()
                ))  
        self.left_up_grid_layout.add_widget(Button(text = "Host/Client mode", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    background_color = (0.1, 0.1, 0.1, 0.05),
                    on_release = lambda a: self.change_mode()
                ))  

        self.right_up_grid_layout = BoxLayout()
        self.right_up_grid_layout.size_hint = (1, None)
        self.right_up_grid_layout.height = 100
        self.add_widget(self.right_up_grid_layout)

        self.right_up_grid_layout.cols = 3
        self.right_up_grid_layout.add_widget(Button(text = "Directory", 
                    color =(1, 1, 1, 1), 
                    background_normal = '', 
                    background_color = (0,0,0,1),                 
                    size_hint = (1, 1), 
                    width = 50,
                    on_press = self.change_label_color,
                    on_release = self.show_directiories
                ))  
        self.right_up_grid_layout.add_widget(Button(text = "Add host", 
                    color =(1, 1, 1, 1), 
                    background_normal = '', 
                    background_color = (0,0,0,1),    
                    size_hint = (1, 1), 
                    width = 50,
                    on_press = self.change_label_color,
                    on_release = self.create_content_frame
                ))      
        self.right_up_grid_layout.add_widget(Button(text = "", 
                    color =(1, 1, 1, 1), 
                    background_normal = '', 
                    background_color = (0,0,0,1),    
                    size_hint = (1, 1), 
                    width = 50
                )) 
        self.right_up_grid_layout.add_widget(Button(text = "Settings", 
                    color =(1, 1, 1, 1), 
                    background_normal = '', 
                    background_color = (0,0,0,1),    
                    background_down = "white", 
                    size_hint = (1, 1),
                    width = 50,
                    on_press = self.change_label_color,
                    on_release = self.create_content_frame
                ))  

        self.left_lower_box_layout = GridLayout()
        self.left_lower_box_layout.cols = 1
        self.left_lower_box_layout.size_hint = (self.left_up_grid_layout.size_hint_x, 1)
        self.left_lower_box_layout.width = Window.width * 0.25
        self.add_widget(self.left_lower_box_layout)

        self.right_lower_grid_layout = GridLayout()
        self.right_lower_grid_layout.cols = 1
        self.right_lower_grid_layout.size_hint = (1, 1) 

        self.add_widget(self.right_lower_grid_layout)

        self.files_manage_bar = GridLayout(size_hint_y=None, height=100, cols=2,rows=1)

        self.right_lower_grid_layout.add_widget(self.files_manage_bar)
        self.refresh_list("Start")

        self.content = GridLayout(size_hint_y=None)
        self.content.size_hint = (1,1)
        self.content.cols = 1

        self.right_lower_grid_layout.add_widget(self.content)

    def change_label_color(self, instance):
        instance.background_color = (1,0,0,1) 

    def create_content_frame(self,instance):
        instance.background_color = (0,0,0,1) 
        self.content.clear_widgets()
        self.content.add_widget(ContentFrame(instance.text))     

    def create_remote_paths_frame(self,first_iteration=False):
        self.files_manage_bar.clear_widgets()
        self.files_manage_bar.add_widget(Button(text = "Upload", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, None), 
                    on_release = lambda a: self.upload_files()
                ))  
                
        self.files_manage_bar.add_widget(Button(text = "Download", 
                    color =(0, 0, 0, 1), 
                    background_normal = '', 
                    size_hint = (1, None), 
                    on_release = lambda a: self.download_files()
                ))  

        self.content.clear_widgets()
        self.scroll_view = ScrollView()

        self.content_scroll_view = GridLayout(size_hint_y=None, row_default_height=60, cols=1)
        self.content_scroll_view.bind(minimum_height=self.content_scroll_view.setter('height'))

        paths = self.sender.get_directories(self.current_path).decode()
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

    def change_drive(self, instance):
        self.current_path = ""
        self.change_path(instance.text)

    def change_path(self,*args,change_drive=False):

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
            self.current_path += args[0].text + "\\"

            self.create_remote_paths_frame(self.current_path)

        self.files_to_download = set()

    def select_files(self,instance):
        path = self.current_path + instance.text

        if path in self.files_to_download:            
            self.files_to_download.remove(path)
            instance.background_color = (1.0, 1.0, 1.0, 1.0)

        else:

            self.files_to_download.add(path)
            instance.background_color = (1.0, 0.0, 0.0, 1.0)


    def connection(self,instance):
        self.connection_thread = Thread(target = self._connection, args=(instance,)) 
        self.connection_thread.start()
    
    def _connection(self,instance):

        def get_address(list_of_devices):
            for name in list_of_devices:
                if name == instance.text:
                    res = list_of_devices[name]

                    return res

        if self.mode == "server":
            self.sender = None
            list_of_devices = get_devices_list()["clients"]

            self.receiver = FileReceiver()
            self.receiver.accept_connections(self.ip_address,4888)

        else:
            if self.sender == None: 
                
                self.receiver = None
                list_of_devices = get_devices_list()["clients"]
                self.sender = FileSender()

                client_info = get_address(list_of_devices)

                self.sender.connect(self.ip_address,client_info[0],client_info[1])
                self.change_path("")


    def connect_with_server(self,addr,port):
        if self.mode == "client":
            self.sender.connect(addr,port)

    def download_files(self):
        
        if len(self.files_to_download) != 0:
            self.sender.get_files(self.files_to_download)
            self.files_to_download = set()

            self.change_path("restore") 

    def upload_files(self):

        dial = FileUploadDialog()
        f_paths = dial.return_file_paths()

        if f_paths != "":
            self.sender.send_files(f_paths)

    def show_directiories(self, instance):
        instance.background_color = (0,0,0,1)
        if self.sender != None:
            self.change_path("restore")

    def stop_server(self):

        try:
            self.receiver.receive_socket.close()
            self.clear_history()
        except:
            pass 
        

    def refresh_list(self,*args):

        def add_list_of_widgets(devices):
            if len(devices) > 0: 
                for device in devices:
                    self.left_lower_box_layout.add_widget(Button(text = device, 
                            color = (0, 0, 0, 1), 
                            background_color = (0.1, 0.1, 0.1, 0.05),
                            size_hint = (1, 1), 
                            pos_hint = {"x":0.35, "y":0.3},
                            on_press = self.connection
                        ))  


        self.left_lower_box_layout.clear_widgets()
        list_of_devices = get_devices_list()

        if self.mode == 'server':
            
            if args[0] == "Start":

                self.left_lower_box_layout.add_widget(Button(text = "Start", 
                        color = (0, 0, 0, 1), 
                        background_normal = '', 
                        background_color = (0.1, 0.1, 0.1, 0.05),
                        size_hint = (1, 1), 
                        pos_hint = {"x":0.35, "y":0.3},
                        width = 50,
                        on_press = self.connection
                    ))  
            elif args[0] == "Stop":

                self.left_lower_box_layout.add_widget(Button(text = "Stop", 
                        color = (0, 0, 0, 1), 
                        background_normal = '', 
                        background_color = (0.1, 0.1, 0.1, 0.05),
                        size_hint = (1, 1), 
                        pos_hint = {"x":0.35, "y":0.3},
                        width = 50,
                        on_press = self.stop_server
                    ))                 

        else:

            add_list_of_widgets(list_of_devices["clients"])

    def clear_history(self):

        self.sender = None
        self.receiver = None
        self.drives = []
        self.drive_letter = ""
        self.current_path = ""
        self.files_to_download = set()

    def change_mode(self):

        if self.mode == 'server':
            self.mode = 'client'

            try:
                self.receiver.receive_socket.close()
            except:
                pass

            self.clear_history()
            self.content.clear_widgets()
            self.refresh_list()

        else:
            self.mode = 'server'

            try:
                self.sender.s.close()
            except:
                pass
            
            self.clear_history()
            self.content.clear_widgets()

            self.refresh_list("Start")

    def add_host(self):
        self.files_manage_bar.clear_widgets()
        self.content.clear_widgets()

    def remove_host(self):
        pass

class GuiApp(App):

    def build(self):
        return MainFrame()

if __name__ == '__main__':

    Window.size = (1280, 720)
    Window.minimum_width, Window.minimum_height = Window.size
    Window.clearcolor = (1, 1, 1, 1)

    GuiApp().run()