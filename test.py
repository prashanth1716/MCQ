import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.button import Button


from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

import json,pickle,base64,os,datetime,subprocess

#variables
question = "what are you doing?"
q_num = 1
options = {"A": "none", "B":"none","C":"none","D":"none"}
answer = "D"
subject = "test"
time_sec = 0
all_num_of_question = 0
data = {}
path = "/"
score = 0

#>>>>>>>>>>>>>>>>>>>>>>>>>>>> files read or update >>>>>>>>>>>>>>>>>>>>>>>

#file read
def file_read():
    global data,subject,all_num_of_question
    try:
        file = open(path,"rb")
        data = pickle.load(file)
        data = base64.standard_b64decode(data)
        data = json.loads(data)
        subject = path[path.rfind("/")+1:path.rfind(".")]
        all_num_of_question = len(data)
    except EOFError:
        warn = Popup(
                title="file error",
                    content=Label(text="file empty"),
                    size_hint = (0.7,0.3)
        )

        warn.open()

#config load
def config_load():
    global subject, all_num_of_question, q_num, score, path, time_sec

    file = open("config.json","r")

    data = json.load(file)

    subject = data["subject"]
    all_num_of_question = data["all_num_of_question"]
    q_num = data["q_num"]
    time_sec = data["time"]
    score = data["score"]
    path = data["path"]

#config write
def config_update():
    file = open("config.json","w")

    data = {"path":path, "subject":subject, "all_num_of_question":all_num_of_question,
            "q_num":q_num, "score":score,"time":time_sec}
    
    json.dump(data,file)

#data load()
def data_load():
    global question,options,answer,q_num

    if q_num <= 0: q_num = 1
    if q_num > all_num_of_question: q_num = all_num_of_question

    question = data[f"Q{q_num}"]["question"]
    options["A"] = data[f"Q{q_num}"]["options"]["A"]
    options["B"] = data[f"Q{q_num}"]["options"]["B"]
    options["C"] = data[f"Q{q_num}"]["options"]["C"]
    options["D"] = data[f"Q{q_num}"]["options"]["D"]
    answer = data[f"Q{q_num}"]["answer"]

#history
def history_save():
    data = {}
    num = 0
    now = datetime.datetime.now()
    try: 
        file = open("history.json","r")
        data = json.load(file)
    except: 
        pass
    
    num = len(data) + 1
    if num == 0: num = 1

    data[f"test{num}"] = {
        "subject":subject,
        "no of questions": all_num_of_question,
        "correct": score,
        "wrong": all_num_of_question-score,
        "time":time_sec,
        "date": f"{now.date()}"
        }
    
    file = open("history.json","w")
    json.dump(data,file,indent=4)

#config restore data
try: config_load()
except: config_update()

#path setup
if len(path.replace(" ",'')) <= 1:
    path = subprocess.Popen(
        ['pwd'], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True
        ).communicate()

    path = path[0].rstrip()
    
    if os.path.exists(path+"/subjects"):
        path = path+"/subjects"
    #elif platform == "android":
    #    path = "/storage/emulated/0/"
    else:
        path = path

    config_update()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>> button actions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class btn:
    #home page
    def home_page_btn(self,instance):
        global q_num
        #exit
        if instance.text == "exit": 
            config_update()
            App.get_running_app().stop()

        #open file
        elif instance.text == "open file":
            self.file_manager()

        #start
        elif instance.text == "Start":
            if os.path.isfile(path):
                self.start = Clock.schedule_interval(self.update_time,1)
                file_read()
                data_load()
                self.question.text = question
                self.option_A.text = options["A"]
                self.option_B.text = options["B"]
                self.option_C.text = options["C"]
                self.option_D.text = options["D"]

                self.q_num_label.text = f"Q{q_num}:"
                instance.text = "next"
                self.next_q.disabled = True

                self.option_A.disabled = False
                self.option_B.disabled = False
                self.option_C.disabled = False
                self.option_D.disabled = False

                if all_num_of_question == q_num: pass
                else:
                    q_num = q_num + 1

                config_update()

            else:
                self.question.text = "select file"
                self.question.color = (0.7,0.1,0.1,0.8)

        #next
        elif instance.text == "next":
            
            #prograss
            if q_num > all_num_of_question:

                h,m,s = 0,0,time_sec
                while True:
                    if s >= 60:
                        m = m + 1
                        s = s - 60
                        if m >= 60:
                            h = h+1
                            m = m - 60
                    else: break

                self.start.cancel()

                main_layout = BoxLayout()
                main_layout.orientation = "vertical"
                head = GridLayout()
                head.cols = 4
                footer = BoxLayout()

                #head
                head.add_widget(Label(text="subject: ", color=(0.7,0.1,0.7,1)))
                head.add_widget(Label(text= subject))

                head.add_widget(Label(text= "no.of questions:", color=(0.7,0.1,0.7,1)))
                head.add_widget(Label(text= str(all_num_of_question)))

                head.add_widget(Label(text="correct:", color=(0.7,0.1,0.7,0.8)))
                head.add_widget(Label(text= str(score)))

                head.add_widget(Label(text="wrong:", color=(0.7,0.1,0.7,0.8)))
                head.add_widget(Label(text= str(all_num_of_question-score), halign="right"))

                head.add_widget(Label(text="time:", color=(0.7,0.1,0.7,0.8)))
                head.add_widget(Label(text= f"{h} : {m} : {s}", halign="right"))

                #footer
                footer.spacing = 10
                footer.size_hint = (1,0.6)

                restart = Button(text="Restart")
                restart.bind(on_press=self.restart)
                new_file = Button(text="New file")
                new_file.bind(on_press=lambda inst: self.file_manager())

                footer.add_widget(restart)
                footer.add_widget(new_file)

                main_layout.add_widget(head)
                main_layout.add_widget(footer)
                
                self.warn = Popup(
                    title="prograss",
                    size_hint=(0.9,0.3),
                    content=main_layout
                )

                self.warn.open()
                
                #self.warn.bind(on_dismiss=self.warn_btn)

            else:
                data_load()
                self.question.text = question
                self.option_A.text = options["A"]
                self.option_B.text = options["B"]
                self.option_C.text = options["C"]
                self.option_D.text = options["D"]

                self.option_A.disabled = False
                self.option_B.disabled = False
                self.option_C.disabled = False
                self.option_D.disabled = False

                q_num = q_num + 1
                self.next_q.disabled = True
                self.q_num_label.text = f"Q{q_num-1}:"
                self.test_sub_num.text = f"{subject}: {score}/{all_num_of_question}"

            config_update()

    #options
    def options_btn(self,instance):
        global score
        #A
        if instance == "A":
            #right answer
            if answer == "A":
                self.correction.text = "corect !!!"
                self.correction.color = (0.1,0.7,0.1,0.8)
                self.option_A.disabled_color = (0.1,0.7,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)
                score = score + 1
            
            #wrong answer
            else:
                self.correction.text = "Wrong !!!"
                self.correction.color = (0.7,0.1,0.1,0.8)

                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)

                if answer == "B":
                    self.option_B.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "C":
                    self.option_C.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "D":
                    self.option_D.disabled_color = (0.1,0.7,0.1,0.8)
          
        #B
        elif instance == "B":
            #right answer
            if answer == "B":
                self.correction.text = "corect !!!"
                self.correction.color = (0.1,0.7,0.1,0.8)
                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.1,0.7,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)
                score = score + 1
            #wrong answer
            else:
                self.correction.text = "Wrong !!!"
                self.correction.color = (0.7,0.1,0.1,0.8)

                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)

                if answer == "A":
                    self.option_A.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "C":
                    self.option_C.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "D":
                    self.option_D.disabled_color = (0.1,0.7,0.1,0.8)

        #C
        elif instance == "C":
            #right answer
            if answer == "C":
                self.correction.text = "corect !!!"
                self.correction.color = (0.1,0.7,0.1,0.8)
                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.1,0.7,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)
                score = score + 1
            #wrong answer
            else:
                self.correction.text = "Wrong !!!"
                self.correction.color = (0.7,0.1,0.1,0.8)

                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)

                if answer == "B":
                    self.option_B.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "A":
                    self.option_A.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "D":
                    self.option_D.disabled_color = (0.1,0.7,0.1,0.8) 

        #D
        elif instance == "D":
            #right answer
            if answer == "D":
                self.correction.text = "corect !!!"
                self.correction.color = (0.1,0.7,0.1,0.8)
                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.1,0.7,0.1,0.8)
                score = score + 1
            #wrong answer
            else:
                self.correction.text = "Wrong !!!"
                self.correction.color = (0.7,0.1,0.1,0.8)

                self.option_A.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_B.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_C.disabled_color = (0.7,0.1,0.1,0.8)
                self.option_D.disabled_color = (0.7,0.1,0.1,0.8)

                if answer == "B":
                    self.option_B.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "C":
                    self.option_C.disabled_color = (0.1,0.7,0.1,0.8)
                elif answer == "A":
                    self.option_A.disabled_color = (0.1,0.7,0.1,0.8) 

        self.option_A.disabled = True
        self.option_B.disabled = True
        self.option_C.disabled = True
        self.option_D.disabled = True

        self.next_q.disabled = False

    #popup btn
    def popup_btn(self,instance):
        global q_num,score,all_num_of_question,time_sec
        #exit
        if instance.text == "exit": self.pop_up.dismiss()

        #open
        if instance.text == "open":
            file_read()
            
            try:
                data["Q1"]
                data["Q1"]["question"]
                data["Q1"]["options"]["A"]
                data["Q1"]["options"]["B"]
                data["Q1"]["options"]["C"]
                data["Q1"]["options"]["D"]
                data["Q1"]["answer"]
                self.pop_up.dismiss()
                q_num = 1
                score = 0
                all_num_of_question = len(data)
                time_sec = 0
                try: self.warn.dismiss()
                except: pass
                history_save()
            except: 
                warn = Popup(
                    title="file error",
                    content=Label(text="wrong data structure"),
                    size_hint = (0.7,0.3)
                )

                warn.open()

            self.next_q.text = "Start"

            config_update()

    #file selection
    def file_selection(self,instance,selection):
        global path
        self.open_file.disabled = False
        try:
            path = selection[0]
        except:
            self.open_file.disabled = True

    #file path
    def path_btn(self,instance,selection):
        global path
        self.open_file.disabled = True
        path = str(selection) + "/"

    #file manager
    def file_manager(self):
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
            path= self.path_btn
        )

        head.add_widget(self.file_chooser)

        #footer
        footer = BoxLayout()
        footer.size_hint = (1,0.150)
        footer.spacing = 10

        pop_exit = Button(
            text="exit",
        )
        pop_exit.bind(on_press=self.popup_btn)
        self.open_file = Button(
            text="open"
        )
        self.open_file.disabled = True
        self.open_file.bind(on_press=self.popup_btn)

        footer.add_widget(pop_exit)
        footer.add_widget(self.open_file)

        layout.add_widget(head)
        layout.add_widget(footer)
            
        self.pop_up = Popup(
            title="select file",
            title_align = "center",
            content=layout,
            size_hint=(0.9,0.7)
        )

        self.pop_up.open()

    #restart
    def restart(self,instance):
        global q_num, score, time_sec
        history_save()
        q_num = 1
        score = 0
        time_sec = 0

        self.warn.dismiss()
        self.next_q.text = "Start"
        config_update()

    def update_time(self,dt):
        global time_sec
        time_sec = time_sec + 1
        h,m,s = 0,0,time_sec

        while s > 60:
            if s >= 60:
                m = m + 1
                s = s - 60
                if m >= 60:
                    h = h+1
                    m = m - 60
            
        self.time.text = f"{h} : {m} : {s}"

        config_update()


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> home page >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class home_page(BoxLayout,btn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        #main layout setup
        self.padding = 15
        self.spacing = 15
        self.orientation = "vertical"

        #layouts
        head = BoxLayout()
        head.size_hint = (1,0.6)
        body = BoxLayout()
        footer = BoxLayout()
        footer.orientation = "vertical"
        footer.spacing = 5

        #>>>>>>>>>>>>>>>>>>>>>>>>>>>>> elements data >>>>>>>>>>>>>>>>>>>>>
        #head
        self.q_num_label = Label(text=f"Q{q_num}:", size_hint = (0.1,1))
        self.question = Label(text=question)

        head.add_widget(self.q_num_label)
        head.add_widget(self.question)

        #body
        grid = GridLayout()
        grid.spacing = 10
        grid.padding = 20
        grid.cols = 2

        #A
        self.option_A = Button(text=f"A: {options['A']}")
        self.option_A.bind(on_press= lambda inst: self.options_btn("A"))
        grid.add_widget(self.option_A)

        #B
        self.option_B = Button(text=f"B: {options['B']}")
        self.option_B.bind(on_press= lambda inst: self.options_btn("B"))
        grid.add_widget(self.option_B)

        #C
        self.option_C = Button(text=f"C: {options['C']}")
        self.option_C.bind(on_press= lambda inst: self.options_btn("C"))
        grid.add_widget(self.option_C)

        #D
        self.option_D = Button(text=f"D: {options['D']}")
        self.option_D.bind(on_press= lambda inst: self.options_btn("D"))
        grid.add_widget(self.option_D)

        self.option_A.disabled = True
        self.option_B.disabled = True
        self.option_C.disabled = True
        self.option_D.disabled = True


        body.add_widget(grid)

        #footer
        footer1 = BoxLayout()
        footer2 = BoxLayout()
        footer2.spacing = 5

        #footer1
        self.time = Label(text="00:00:00",size_hint=(1,0.6))
        self.correction = Label(text="wel come!",size_hint=(1,0.6))
        self.test_sub_num = Label(text=f"{subject}: {score}/{all_num_of_question}",size_hint=(1,0.6))

        footer1.add_widget(self.time)
        footer1.add_widget(self.correction)
        footer1.add_widget(self.test_sub_num)

        #footer2
        stop_exit = Button(text="exit",size_hint=(1,0.6))
        open_file = Button(text="open file",size_hint=(1,0.6))
        self.next_q = Button(text="Start",size_hint=(1,0.6))

        stop_exit.bind(on_press=self.home_page_btn)
        open_file.bind(on_press=self.home_page_btn)
        self.next_q.bind(on_press=self.home_page_btn)

        footer2.add_widget(stop_exit)
        footer2.add_widget(open_file)
        footer2.add_widget(self.next_q)

        footer.add_widget(footer1)
        footer.add_widget(footer2)

        #add to main layout
        self.add_widget(head)
        self.add_widget(body)
        self.add_widget(footer)
        
#>>>>>>>>>>>>>>>>>>>>>>>>>> class of app (run)>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class testapp(App):
    def build(self):
        return home_page()
    
if __name__ == "__main__":
    testapp().run()