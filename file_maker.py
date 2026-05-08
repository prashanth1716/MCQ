#kivy files
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import sp

from kivy.core.window import Window
from kivy.utils import platform

#file loader file
import base64,pickle,json,subprocess,os

'''<<<<<<<<<<<<< file structure >>>>>>>>>>>>>>>>>>>>>
Q1:{"question": "what is your name?",
"options": {"A": None, "B": None, "C": None, "D":None},
"answer":A}
'''

#>>>>>>>>>>>>>>>>>>>>>> variables >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

font_size = sp(15)
size = (0.3,0.6)

path = ""
mcq_num = 1
q = ""
options = {}
answer = ""
data = {}

#update
def config_update():
    data = {}
    data["path"] = path
    data["mcq_num"] = mcq_num

    file = open("config_maker.json","w")
    json.dump(data,file)

#load
def config_load():
    global path,mcq_num

    file = open("config_maker.json","r")
    data = json.load(file)

    path = data["path"]
    mcq_num = data["mcq_num"]

#file read
def file_read():
    global mcq_num
    file = open(path,"rb")
    
    data = pickle.load(file)
    data = base64.standard_b64decode(data)
    data = json.loads(data)

    if len(data) != 0:
        mcq_num = len(data)+1
    else:
        mcq_num = 1

    return data

def file_write():   
    data = {}
    try:
        data = file_read()
    except: 
        data = {}

    file = open(path,"wb")
    
    data["Q"+str(mcq_num)] = {
        "question":q,
        "options":options,
        "answer":answer
    }

    data = json.dumps(data).encode(encoding="utf-8")
    data = base64.standard_b64encode(data)
    pickle.dump(data,file)

try: config_load()
except: print("file error")

#path fix
if len(path.replace(" ","")) < 1:
    path = subprocess.Popen(
        ['pwd'], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
        ).communicate()

    path = path[0].rstrip()

    
    if os.path.isdir(path+"/subjects/"):
        path = path+"/subjects/"
    #elif platform == "android":
    #    path = "/storage/emulated/0"
    else:
        path = path

if os.path.isfile(path):
    pass
else:
    path = subprocess.Popen(
        ['pwd'], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
        ).communicate()

    path = path[0].rstrip()

    
    if os.path.isdir(path+"/subjects/"):
        path = path+"/subjects/"
    elif platform == "android":
        path = "/storage/emulated/0"
    else:
        path = "/"

try: file_read()
except: pass

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> button bind >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class button_action:
    #home page buttons 
    def homepage_btn(self,instance):
        self.path = ""
        global path,mcq_num,q,options,answer
        #exit
        if instance.text == "Exit":
            config_update()
            App.get_running_app().stop()

        #file open
        elif instance.text == "Open file":

            layout = BoxLayout()
            layout.orientation = "vertical"

            #head
            head = BoxLayout()
            head.size_hint = (1,1)
            self.file_chooser = FileChooserListView(
                filters=["*.pkl"],
                path=path
            )
            self.file_chooser.bind(
                selection = self.file_selection,
                path= self.file_path
            )

            head.add_widget(self.file_chooser)

            #footer
            footer = BoxLayout()
            footer.size_hint = (1,0.150)
            footer.spacing = 10

            pop_exit = Button(
                text="exit",
                font_size = font_size,
                size_hint = size
            )
            pop_exit.bind(on_press=self.popup_btn)
            create_file = Button(
                text="create",
                font_size = font_size,
                size_hint = size
            )
            create_file.bind(on_press=self.popup_btn)
            self.open_file = Button(
                text="open",
                font_size = font_size,
                size_hint = size
            )
            self.open_file.disabled = True
            self.open_file.bind(on_press=self.popup_btn)

            footer.add_widget(pop_exit)
            footer.add_widget(create_file)
            footer.add_widget(self.open_file)

            layout.add_widget(head)
            layout.add_widget(footer)
            
            self.pop_up = Popup(
                title="select file",
                title_align = "center",
                content=layout,
                size_hint=(0.9,0.8)
            )

            self.pop_up.open()

        #save
        elif instance.text == "Save":

            msg = Popup(
                title="select file",
                title_align = "center",
                content=Label(text="saved",font_size=font_size+2),
                size_hint=(size[0]+0.4, size[1]-0.2)
            )
        
            path = "/"
            mcq_num = 1

            if len(path.replace(" ","")) <= 1:
                path = subprocess.Popen(
                    ['pwd'], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True
                    ).communicate()

                path = path[0].rstrip()

                if os.path.isdir(path+"/subjects/"):
                    path = path+"/subjects/"
                elif platform == "android":
                    path = "/storage/emulated/0"
                else:
                    path = "/"

            self.save_btn.disabled = True
            self.Next_btn.disabled = True

            self.path_label.text = "select file"

            self.question.text = ""
            self.option_A.text = ""
            self.option_B.text = ""
            self.option_C.text = ""
            self.option_D.text = ""

            self.checkbox_A.active = True
            self.checkbox_A.active = False

            config_update()

            msg.open()
            
        #next btn
        elif instance.text == "Next":
    
            #question
            if len(self.question.text.replace(" ","")) == 0:
                self.question.hint_text_color = (0.6,0.1,0.1,0.6)
                self.question.hint_text = "Enter question"
                return 0
            else: q = self.question.text

            #options
            if len(self.option_A.text.replace(" ","")) == 0:
                self.option_A.hint_text_color = (0.6,0.1,0.1,0.6)
                self.option_A.hint_text = "Enter 'A'"
                return 0
            else: options['A'] = self.option_A.text

            if len(self.option_B.text.replace(" ","")) == 0:
                self.option_B.hint_text_color = (0.6,0.1,0.1,0.6)
                self.option_B.hint_text = "Enter 'B'"
                return 0
            else: options['B'] = self.option_B.text

            if len(self.option_C.text.replace(" ","")) == 0:
                self.option_C.hint_text_color = (0.6,0.1,0.1,0.6)
                self.option_C.hint_text = "Enter 'C'"
                return 0
            else: options['C'] = self.option_C.text

            if len(self.option_D.text.replace(" ","")) == 0:
                self.option_D.hint_text_color = (0.6,0.1,0.1,0.6)
                self.option_D.hint_text = "Enter 'D'"
                return 0
            else: options['D'] = self.option_D.text

            #answer
            if len(answer.replace(" ","")) == 0:
                self.answer_label.color = (0.6,0.1,0.1,0.6)
                self.answer_label.text = "select"
                return 0
            else:
                pass

            file_write()
            mcq_num = mcq_num + 1
            self.question_number.text = f"Q{mcq_num}"

            self.question.text = ""
            self.option_A.text = ""
            self.option_B.text = ""
            self.option_C.text = ""
            self.option_D.text = ""

            self.checkbox_A.active = True
            self.checkbox_A.active = False

            config_update()

    #pop up btns
    def popup_btn(self,instance):
        #exit
        if instance.text == "exit": self.pop_up.dismiss()

        #create
        elif instance.text == "create":
            layout = BoxLayout()
            layout.orientation = "vertical"
            layout.padding = 5
            layout.spacing = 20
            
            #head
            head = BoxLayout()
            head.size_hint = (1,0.8)
            self.file_name = TextInput(
                hint_text="file name",
                font_size=font_size,
                size_hint = (0.2,size[1])
            )
            head.add_widget(self.file_name)

            #footer
            footer = BoxLayout()
            footer.spacing = 10
            #cancel
            cancel = Button(
                text="cancel",
                font_size=font_size,
                size_hint = size
                )
            cancel.bind(on_press=self.filename_btn)
            #create
            create = Button(
                text="create",
                font_size = font_size,
                size_hint = size
            )
            create.bind(on_press=self.filename_btn)

            footer.add_widget(cancel)
            footer.add_widget(create)


            #add to main layout
            layout.add_widget(head)
            layout.add_widget(footer)

            #file name popup
            self.popup_filename = Popup(
                title = "only .pkl",
                title_align = "center",
                content=layout,
                size_hint = (0.7,0.4)
            )

            self.popup_filename.open()

        #opem
        elif instance.text == "open":
            global path,mcq_num
            path = self.path
            self.save_btn.disabled = False
            self.Next_btn.disabled = False
            try: 
                data = file_read()
                data["Q1"]
                data["Q1"]["question"]
                data["Q1"]["options"]["A"]
                data["Q1"]["options"]["B"]
                data["Q1"]["options"]["C"]
                data["Q1"]["options"]["D"]
                data["Q1"]["answer"]

            except: mcq_num = 1

            config_update()
            
            self.question_number.text = f"Q{mcq_num}"
            self.pop_up.dismiss()
            as_name = path[path.rfind("/")+1:]
            self.path_label.text = as_name[:path.rfind(".")]

    #file 
    def filename_btn(self,instance):
        if instance.text == "cancel":self.popup_filename.dismiss()
        
        elif instance.text == "create":
            global path
            if path.count(".") >= 1:
                path = path[:str(path).rfind("/")] + "/"

            file_name = str(self.file_name.text)
            file_name = file_name.replace(" ","_").replace("/","")
            if len(file_name) > 1:

                if file_name.count(".") == 0: 
                    file_name = file_name+".pkl"
                    self.popup_filename.dismiss()

                elif file_name.count(".") == 1:
                    if file_name[file_name.find(".")+1:] == "pkl":
                        file_name = file_name
                        self.popup_filename.dismiss()
                    else:
                        self.file_name.text = ""
                        self.file_name.hint_text = "only .pkl"
                        self.file_name.hint_text_color = (0.8,0.1,0.1,0.6)
                        file_name = ""

                elif file_name.count(".") > 1:
                    self.file_name.text = ""
                    self.file_name.hint_text = "use only single '.'"
                    self.file_name.hint_text_color = (0.8,0.1,0.1,0.6)
                    file_name = ""

                if len(file_name) > 4:
                    if os.path.isfile(path):pass
                    else:
                        file = open(path+file_name,"w")
                        file.close()
                        self.file_chooser.path = path
                
    #file path by filechooser
    def file_path(self,instance,selection):
        self.open_file.disabled = True
        self.path = str(selection) + "/"

    def file_selection(self,instance,selection):
        self.open_file.disabled = False
        try:
            self.path = selection[0]
        except:
            self.open_file.disabled = True
        
    #window exit btn
    def close_btn(self,*args):
        config_update()
        App.get_running_app().stop()
    
    #checkbox
    def checkbox_select(self,instance,value):
        global answer
        if value:
            self.answer_label.color = (0.7,0.7,0.7,0.7)
            self.answer_label.text = "answer"
            answer = instance
        else:
            answer = ""

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> home page >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class home_page(BoxLayout,button_action):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #window exit btn
        Window.bind(on_request_close=self.close_btn)

        #setup
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 20

        #>>>>>>>>>>>>>>>>>>>>>>>>> head layer >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        head_layer = BoxLayout()
        head1 = BoxLayout()
        head2 = BoxLayout()

        #setup
        head_layer.orientation="vertical"
        head_layer.size_hint = (1,0.7)

        #elements
        self.path_label = Label(
            text="select file",
            font_size=font_size
            )
        
        self.question_number = Label(
            text=f"Q{mcq_num}",
            size_hint=(0.1,1),
            font_size=font_size
            )
        
        self.question = TextInput(
            hint_text="Question",
            font_size=font_size
        )

        #add to layout
        head1.add_widget(self.path_label)
        head2.add_widget(self.question_number)
        head2.add_widget(self.question)

        head_layer.add_widget(head1)
        head_layer.add_widget(head2)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> body layer >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        body_layer = BoxLayout()
        option_layout = GridLayout()

        #setup
        option_layout.cols = 2
        option_layout.spacing = 10

        #elements
        #A
        self.option_A = TextInput(
            hint_text="option 'A'",
            font_size=font_size,
            size_hint = size
        )
        option_layout.add_widget(self.option_A)

        #B
        self.option_B = TextInput(
            hint_text="option 'B'",
            font_size=font_size,
            size_hint = size
        )
        option_layout.add_widget(self.option_B)

        #C
    
        self.option_C = TextInput(
            hint_text="option 'C'",
            font_size=font_size,
            size_hint = size
        )
        option_layout.add_widget(self.option_C)

        #D
        
        self.option_D = TextInput(
            hint_text="option 'D'",
            font_size=font_size,
            size_hint = size
        )
        option_layout.add_widget(self.option_D)


        #add to layout
        body_layer.add_widget(option_layout)

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> footer layer >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        footer_layer = BoxLayout()
        footer1 = BoxLayout()
        footer2 = BoxLayout()

        #setup
        footer_layer.orientation = "vertical"
        footer2.spacing = 10

        #elements
        #footer1
        self.answer_label = Label(
            text="answer: ",
            font_size=font_size
            )
        footer1.add_widget(self.answer_label)

        #A
        footer1.add_widget(Label(
            text="A",
            font_size=font_size
            ))
        self.checkbox_A = CheckBox(
            group="options"   
        )
        self.checkbox_A.bind(active= lambda inst,val: self.checkbox_select("A",val))
        footer1.add_widget(self.checkbox_A)

        #B
        footer1.add_widget(Label(
            text="B",
            font_size=font_size
            ))
        self.checkbox_B = CheckBox(
            group="options"   
        )
        self.checkbox_B.bind(active= lambda inst,val: self.checkbox_select("B",val))
        footer1.add_widget(self.checkbox_B)

        #c
        footer1.add_widget(Label(
            text="C",
            font_size=font_size
            ))
        self.checkbox_C = CheckBox(
            group="options"   
        )
        self.checkbox_C.bind(active= lambda inst,val: self.checkbox_select("C",val))
        footer1.add_widget(self.checkbox_C)

        #D
        footer1.add_widget(Label(
            text="D",
            font_size=font_size
            ))
        self.checkbox_D = CheckBox(
            group="options"   
        )
        self.checkbox_D.bind(active= lambda inst,val: self.checkbox_select("D",val))
        footer1.add_widget(self.checkbox_D)

        #footer2 
        exit_btn = Button(
            text="Exit",
            font_size=font_size,
            size_hint = size
            )
        exit_btn.bind(on_press=self.homepage_btn)
        
        open_file = Button(
            text="Open file",
            font_size=font_size,
            size_hint = size
            )
        open_file.bind(on_press=self.homepage_btn)
        
        self.save_btn = Button(
            text="Save",
            font_size=font_size,
            size_hint = size
            )
        if path[-3:] == "pkl": self.save_btn.disabled = False
        else: self.save_btn.disabled = True
        self.save_btn.bind(on_press=self.homepage_btn)

        self.Next_btn = Button(
            text="Next",
            font_size=font_size,
            size_hint = size
            )
        if path[-3:] == "pkl": self.Next_btn.disabled = False
        else: self.Next_btn.disabled = True
        self.Next_btn.bind(on_press=self.homepage_btn)
        
        footer2.add_widget(exit_btn)
        footer2.add_widget(open_file)
        footer2.add_widget(self.save_btn)
        footer2.add_widget(self.Next_btn)

        #add to layout
        footer_layer.add_widget(footer1)
        footer_layer.add_widget(footer2)

        #add to main layout
        self.add_widget(head_layer)
        self.add_widget(body_layer)
        self.add_widget(footer_layer)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> App class >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class file_maker(App):
    def build(self):
        return home_page()
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> run command >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
if __name__ == "__main__":
    #file_maker().run()
    try:
        file_maker().run()
    except:
        config_update()
        file_maker().stop()
