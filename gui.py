from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.config import Config
from kivy.core.window import Window
from subprocess import Popen, PIPE
from kivy.lang import Builder
import kivy.properties as kyprops
from kivy.uix.scrollview import ScrollView

from app import FileTransfer


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




class MainFrame(GridLayout):

    def __init__(self, **kwargs):
        super(MainFrame, self).__init__(**kwargs)

        self.mode = "client"

        self.transfer_app = FileTransfer()

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
                    on_release = lambda a: self.create_settings_frame()
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
        self.refresh_list()

        self.right_lower_grid_layout = GridLayout()
        
        self.right_lower_grid_layout.cols = 1
        self.right_lower_grid_layout.size_hint = (1, 1) # co to robi

        self.add_widget(self.right_lower_grid_layout)

        self.files_manage_bar = GridLayout(size_hint_y=None, height=100)
        self.files_manage_bar.cols = 2
        self.files_manage_bar.row = 1

        self.right_lower_grid_layout.add_widget(self.files_manage_bar)


        

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


        self.create_remote_paths_frame()

        

    def create_settings_frame(self):

        self.content.clear_widgets()
        self.content.add_widget(Label(text='Settings', color=(0,0,0,1)))     


    def create_remote_paths_frame(self):

        self.content.clear_widgets()
        self.scroll_view  = ScrollView()

        self.content_scroll_view = GridLayout(size_hint_y=None, row_default_height=60, cols=1)
        self.content_scroll_view.bind(minimum_height=self.content_scroll_view.setter('height'))


        paths = ["A:\\","B:\\","C:\\","D:\\","E:\\","F:\\","G:\\","H:\\","I:\\","J:\\","K:\\","L:\\","M:\\","N:\\"]

        for path in paths:

            self.content_scroll_view.add_widget(Button(text = path, 
                    color =(0, 0, 0, 1), 
                    size_hint = (1, None), 
                    on_press = self.select_files
                ))  

        self.scroll_view.add_widget(self.content_scroll_view)

        self.content.add_widget(self.scroll_view)

        
        # self.content.add_widget(Label(text='test', color=(0,0,0,1)))     

    def select_files(self,instance):

        if instance.text in self.files_to_download:            
            self.files_to_download.remove(instance.text)
            instance.background_color = (1.0, 1.0, 1.0, 1.0)

        else:

            self.files_to_download.add(instance.text)
            instance.background_color = (1.0, 0.0, 0.0, 1.0)


        print(self.files_to_download)

        


    def download_files(self):

        pass

    def upload_files(self):

        pass

    def refresh_list(self):

        def add_list_of_widgets(list_of_names):

            if len(list_of_names) > 0: 
                for name in list_of_names:
                    self.left_lower_box_layout.add_widget(Button(text = name, 
                            color = (0, 0, 0, 1), 
                            background_normal = '', 
                            size_hint = (1, 1), 
                            pos_hint = {"x":0.35, "y":0.3},
                            width = 50
                        ))  


        self.left_lower_box_layout.clear_widgets()
        list_of_devices = self.transfer_app.get_devices_list()

        if self.transfer_app.mode == 'client':
            
            add_list_of_widgets(list_of_devices["hosts"])

        else:

            add_list_of_widgets(list_of_devices["clients"])


    def change_mode(self):

        if self.transfer_app.mode == 'host':
            self.transfer_app.mode = 'client'
        else:
            self.transfer_app.mode = 'host'
        
        self.refresh_list()

class GuiApp(App):

    def build(self):
        return MainFrame()

if __name__ == '__main__':

    Window.size = (1280, 720)
    Window.minimum_width, Window.minimum_height = Window.size
    Window.clearcolor = (1, 1, 1, 1)

    GuiApp().run()