from tkinter import HORIZONTAL
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import * 
from getting_pitch import Getting_pitch
from database import Database
from audio import recording
import math
import tkinter.messagebox as mb


class general_methods():

    def __init__(self):
        self.chosen_tuning_name=""
        self.database = Database()
    

    def start_up (self): #connects to database and sets the tuning to the first tuning in the database

        database_object= Database()
        database_object.check_exist()
        tuning_names=database_object.retrieve_database_collum("Tuning_name")
        try:
            self.intial_tuning_name = str(tuning_names[0])
        except:
            print("No Tuning Found")


    def get_tuning_name(self):

        return self.intial_tuning_name



class App_interface(tk.Tk,general_methods):

    def __init__(self):
        self.start_up()
        super().__init__()
        self.title("Guitar Tuner")
        self.center_screen()
  

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        try:        
            tuning_name=self.get_tuning_name()
        except:
            tuning_name =None
        
        # Configure grid weights so frames expand to fill screen
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None

        self.frames={}

        for Page in (main_menu, Tuning_editor, Tuning_interface, Edit_or_choose_tuning, Tuning_list):
            if Page == main_menu or Page ==Tuning_list or Page == Tuning_interface:
                frame = Page(controller=self, parent=container,chosen_tuning_name=tuning_name)
            else:
                frame = Page(parent=container, controller=self)
            self.frames[Page] = frame
            frame.grid(column=0, row=0, sticky="nsew")

        # Display the main menu on startup
        self.show_frame(main_menu)

    def show_frame(self, Page):

        if self.current_frame is not None and hasattr(self.current_frame, "on_hide"):
            self.current_frame.on_hide()

        frame = self.frames[Page]
        frame.tkraise()  
        self.current_frame = frame

        if hasattr(frame, "on_show"):
            frame.on_show()

    
    def center_screen(self):
        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_heigth = self.winfo_screenheight()

        self.geometry(f"{screen_width}x{screen_heigth}+0+0")




class main_menu(tk.Frame,general_methods):



    def __init__(self,parent, controller,chosen_tuning_name):
        super().__init__(parent, bg="lightblue")

        self.chosen_tuning_name=chosen_tuning_name
        self.controller =controller
        self.current_tuning=""
        self.database=Database()
        header_frame = tk.Frame(self, bg="lightblue")
        header_frame.pack(side="top",fill = "x", pady=10)
        tune_button=tk.Button(self, 
                           text="Tune",
                           width=15,
                           height=2,
                           font=("arial",20),
                           command=self.open_tuning_interface,
                           bg="white"                   
        )

        welcome_label=tk.Label(header_frame,
                               text="Welcome To Pitch Perfect Tuner!",
                               font=("arial",25,"bold"),
                               bg="lightblue",
                               height= 3
        )

        database_button = tk.Button(self,
                                    text= "Choose or Edit Tuning",
                                    width=20,
                                    height=2,
                                    font=("arial",20),
                                    command=self.open_database_menu,
                                    bg="white")
        
        self.current_tuning_display = tk.Label(header_frame,
                                          text = self.current_tuning,
                                          width =27,
                                          height = 2,
                                          font = ("arial",20),
                                          bg = "white"
                                          )
         
        tuning_label= tk.Label(header_frame,
                               text = "Current Tuning",
                               width = 20,
                               height=1,
                               font=("arial",16),
                               bg="lightblue")
                                    

        welcome_label.pack(side="top",pady=10)
        self.current_tuning_display.pack(side = "top", expand = True, padx=2 )
        tuning_label.pack(side ="top",expand=True, padx=2)
        database_button.pack(expand=True,side="left",padx=2)
        tune_button.pack(expand=True,side="right",padx=1,pady=5)



    def open_tuning_interface(self):
        self.database.close_connection()
        self.controller.show_frame(Tuning_interface)


    def open_database_menu(self):
        self.database.close_connection()
        self.controller.show_frame(Edit_or_choose_tuning)


    def on_show(self):
        self.database.check_exist()
        self.current_tuning=""
        self.update_label()



    def on_hide(self):
        self.database.close_connection()



    def recieve_tuning (self,tuning_name):

        self.chosen_tuning_name=tuning_name
        self.update_label()



    def update_label (self):
        
        try:
            notes, octaves = self.database.retrive_tuning(self.chosen_tuning_name)
            if notes is None or octaves is None:
                # If tuning doesn't exist, use default values
                self.current_tuning = "No tuning selected"
            else:
                for i in range (0,len(notes)):
                    self.current_tuning +=( f"{notes[i]} {octaves[i]}, ")
        except Exception as e:
            print(f"Error: No Tuning selected")
            self.current_tuning = "retrieval error"
        self.current_tuning_display.config(text="")
        self.current_tuning_display.config(text=self.current_tuning)






class Tuning_interface(tk.Frame,general_methods):


 
    def __init__(self,parent,controller,chosen_tuning_name):

        super().__init__(parent, bg="lightblue")

        self.database=Database()
        self.controller =controller
        self.tuning_name=chosen_tuning_name
        self.audio_import=Getting_pitch()
        self.pitch = 0
        self.update_job = None 
        self.tuning_data_retrival()
        self.list_string_button=[]
        self.target_pitch=None
        self.filtered_bar_value = 50
        self.filter_strength = 0.2
        self.audio_import.getting_pitch_start()

        self.bar=Progressbar(self,
                        orient=HORIZONTAL,
                        length=1000,
                        mode="indeterminate",)
        
        back_to_main_menu=tk.Button(self,
                                    width=20,
                                    height=3,
                                    font=("arial",14),
                                    text="Back To Main Menu",
                                    command=self.return_to_main_menu)
        
        self.hertz_value = tk.Label(self,
                               text = f"{self.pitch} Hz",
                               font = ("arial",24,"bold"),
                               bg = "lightblue",
                               fg = "red",
                               width = 15,
                               
                            )
        self.hertz_value.pack(pady=10)

        self.string_label = tk.Label(self,
                                    text="No string selected",
                                    font=("arial",16),
                                    bg="lightblue")
        
        self.string_label.pack(pady=(0,10))

        #generates the buttons for each string
        btn_frame = tk.Frame(self, bg="lightblue")
        btn_frame.pack(pady=(0,20))

        for i in range(1,7):
            string_button = tk.Button(btn_frame, text=f"String {i}", width=10,
                          command=lambda idx=i: self.select_string(idx))
            string_button.grid(row=0, column=i-1, padx=5)
            self.list_string_button.append(string_button)

        
        back_to_main_menu.pack(expand=True,side="bottom")

        self.bar["value"]=0

    def on_show(self):
        self.run =True
        self.audio_import.getting_pitch_start()
        self.bar.pack(pady=100,side="top")
        self.update_job = self.after(100, self.update_bar)


    def on_hide(self):
        self.run = False
        self.audio_import.stop()


    def update_bar(self):
    
        if self.run==True:
            self.pitch =self.audio_import.getting_pitch_extraction()
            self.update_hertz_value()


            bar_value = self.tuning_bar_scaling()
            filtered_value = self.low_pass_filter(bar_value)
            self.bar["value"] = filtered_value

            self.is_in_tune()
            self.update_job = self.after(50, self.update_bar)


    def update_hertz_value(self):

        self.hertz_value.config(text = f"{round(self.pitch, 1)} Hz")


    def return_to_main_menu(self):
        # Cancel any pending after() calls
        self.controller.show_frame(main_menu)



    def recieve_tuning(self,tuning_name):

        self.tuning_name=tuning_name
        self.tuning_data_retrival()
        self.update_tuning_button_values()


    def tuning_data_retrival (self):
        
        self.notes, self.octaves = self.database.retrive_tuning(self.tuning_name)

    
    def tuning_bar_scaling(self):
        
        if not hasattr(self, "target_pitch") or self.pitch <= 0 or self.target_pitch == None:
            return 50  # centre when no pitch

        cents = 1200 * math.log2(self.pitch / self.target_pitch)

        # ±50 cents maps to 0–100
        bar_value = 50 + cents/2

        # clamp
        bar_value = max(0, min(100, bar_value))
        return bar_value
    
    def low_pass_filter (self, new_value, filter_strength = 0.1 ):

        self.filtered_bar_value = (filter_strength * new_value + (1- filter_strength) * self.filtered_bar_value)
        return self.filtered_bar_value


    def select_string(self, index):

        try:
            if not hasattr(self, "notes") or index-1 >= len(self.notes):
                self.string_label.config(text="Invalid string / tuning data missing")
                self.target_pitch=0
                return
        except:
            self.string_label.config(text="Invalid string / tuning data missing")
            self.target_pitch=0
            return
        
        note = self.notes[index-1]
        octave = self.octaves[index-1]
        freq = self.note_to_frequency(note, octave)

        self.selected_string = index
        self.target_pitch = freq
        self.string_label.config(text=f"String {index} -> {note} {octave} ({round(freq,2)} Hz)")


    def note_to_frequency (self,note,octave):
        
        pitch_values=self.database.CORROSPONDING_FREQUENCIES
        note_list=self.database.VALID_VALUES
        for i in range(0,len(note_list)-1):
            if note == note_list[i]:
                base_pitch=pitch_values[i]
        target_pitch = base_pitch*(2**octave)
        return target_pitch
    

    def update_tuning_button_values(self):

        for i, button in enumerate(self.list_string_button):
            if i <len(self.notes):
                note =self.notes[i]
                octave = self.octaves[i]
                button.config(text=f"{note}{octave}")
            else:
                button.config(text="N/A")

    def is_in_tune(self):

        try:
            if self.pitch <= self.target_pitch+0.2 or self.pitch >= self.target_pitch - 0.2:
                self.hertz_value.config(fg="red")
            else:
                self.hertz_value(fg="green")
        except:
            self.hertz_value.config(fg="red")





class Tuning_editor (tk.Frame,general_methods):


    def __init__(self,parent,controller):
        super().__init__(parent, bg="lightblue")

        self.controller =controller
        self.database=Database()
        self.new_tuning=True
        note_list=[]
        self.final_tuning= {1:None,2:None,3:None,4:None,5:None,6:None}
        self.final_tuning_display = (", ".join(str(v) for v in self.final_tuning.values())) # formats the dictionary into a printable list

        self.database_organiser = tk.Frame(self, bg="lightblue")
        self.database_organiser.pack(side="left",fill="y")

        self.tunings_list=tk.Listbox(self.database_organiser,selectmode=tk.SINGLE, font=("arial",18),width=30)
        self.tunings_list.pack(padx=(35,0),side="left",fill="y",expand=False,pady=40)

        tuning_name_list=self.database.retrieve_database_collum("Tuning_name")
        for names in tuning_name_list:
            self.tunings_list.insert(tk.END,names)

        new_tuning_button=tk.Button(self.database_organiser,
                                   text="Create New Tuning",
                                   font=("arial",16),
                                   height=3,
                                   width=15,
                                   command=self.create_new_tuning)
        
        new_tuning_button.pack(pady=(150,10),padx=(30,0),side="top")

        edit_tuning_button=tk.Button(self.database_organiser,
                                    text="Edit Tuning",
                                    font=("arial",16),
                                    height=3,
                                    width=15, 
                                    command=self.edit_tuning)
        
        edit_tuning_button.pack(pady=200,padx=(30,0),side="top")

        delete_tuning_button = tk.Button(self.database_organiser,
                                text = "Delete Tuning",
                                font = ("arial",16),
                                height = 3,
                                width = 15,
                                command = self.delete_tuning )

        delete_tuning_button.pack( padx=(30,0),side="top")


        notes=self.database.value_retrieval() # creates all combonations of note and octave
        for octaves in range (1,5):
            for note in notes:
                note_list.append(f"{note} {octaves}" )

        top_container = tk.Frame(self, bg="lightblue")
        top_container.pack(pady=20, padx=(0,10), anchor="n")


        choice_frame = tk.Frame(self, bg="lightblue") # groups the comboboxes together 
        choice_frame.pack(pady=(20,0),side="right",padx=(0,20))

        name_input_frame = tk.Frame(self, bg = "lightblue" )
        name_input_frame.pack(pady = 20, padx = (0,10),anchor = "center" )

        confirm_new_tuning_button = tk.Button(name_input_frame,
                                                text="Confirm New Tuning",
                                                font=("arial",16),
                                                command=self.tuning_complete)

        for i in range (1,7): # loops the combobox creation for all 6 strings

            individual_frame = tk.Frame(self, bg="lightblue")
            individual_frame.pack(pady=20,anchor="e")

            string_notation = tk.Label(individual_frame,
                                        text=f"String {i}", 
                                        font=("arial",12), 
                                        bg = "lightblue")
            string_notation.pack()

            self.note_choice = ttk.Combobox(individual_frame,
                                font=("arial",12),
                                values= note_list,
                                state = "readonly")
            
            self.note_choice.set("select a note")
            self.note_choice.pack(side="left",padx=(0,10))
            
            conformation = tk.Button(individual_frame,
                                     font=("arial",12),
                                     text="Confirm",
                                     command=lambda idx=i,
                                     c=self.note_choice: self.confirm_choice(idx, c)
                                     )
            
            conformation.pack(expand=True, side="left", padx=(0,10))

        self.tuning_display = tk.Label(top_container,           # displays the current selected notes
                                        font = ("arial",18),
                                         text = f"{self.final_tuning_display}",
                                         height= 1,
                                         width = 30
                                         )
        self.tuning_display.pack(side = "top",anchor= "n",pady=20,padx=(0,1))

        back_to_main_menu=tk.Button(self,
                                    width=20,
                                    height=3,
                                    font=("arial",14),
                                    text="Back To Main Menu",
                                    command=self.return_to_main_menu
                                    
        )
        back_to_main_menu.pack(side = "bottom", pady=30)

        self.tuning_namer_box = tk.Entry(name_input_frame,
                                        font=("arial",18),
                                        width = 30,
                                        justify="center")
        
        self.tuning_namer_box.pack(pady = 10,padx=50)
        tuning_namer_label = tk.Label(name_input_frame,
                                      font=("arial",14),
                                      text="Tuning Name",
                                      bg = "lightblue",
                                      width = 30 )
        tuning_namer_label.pack(side="top")
        confirm_new_tuning_button.pack(side="bottom",pady=(20,0))



    def return_to_main_menu(self):
        
        self.controller.show_frame(main_menu)


    def confirm_choice(self,index, string_x):
        
        note=string_x.get()
        if note == "select a note":
            pass
        else:
            print(f"string {index} selected {note}")
            self.final_tuning[index] = note # replaces the note with the users choice
            self.update_final_tuning()
            
    
    def update_final_tuning(self):

        self.final_tuning_display = (", ".join(str(v) for v in self.final_tuning.values()))
        self.tuning_display.config(text= self.final_tuning_display)
        self.update_database_list


    def create_new_tuning(self):
        
        self.tuning_namer_box.delete(0,tk.END) # clears the naming box for new tuning
        self.new_tuning=True
        self.final_tuning= {1:None,2:None,3:None,4:None,5:None,6:None}
        self.final_tuning_display = (", ".join(str(v) for v in self.final_tuning.values()))
        self.update_final_tuning()
        self.update_database_list()
        

    
    def edit_tuning(self):

        self.tuning_namer_box.delete(0,tk.END) # clears the naming box to load chosen tuning
        tuning_values= ""
        self.new_tuning=False
        name_index=self.tunings_list.curselection()
        if name_index:
            name_index = name_index[0]
            self.original_tuning_name=self.tunings_list.get(name_index)
            notes, octaves = self.database.retrive_tuning(self.original_tuning_name)
            for i in range (0,len(notes)):
                tuning_values += f"{notes[i]} {octaves[i]}, "
                self.final_tuning[i+1]= f"{notes[i]} {octaves[i]}"

            self.tuning_namer_box.insert(0,self.original_tuning_name)
            

            self.tuning_display.config(text=tuning_values)

        else:
            print("Error: No Tuning selected")
        self.update_database_list()


    def tuning_complete(self):

        tuning_proper_format=[]
        can_continue=True
        for i in range (1,7):
            if self.final_tuning[i] == None:
                can_continue=False

        if can_continue== True:

            for string_number, value in self.final_tuning.items(): # seperates note and octave for database insertion
                
                note, octave = str(value).split(" ")
                tuning_proper_format.append(note)
                tuning_proper_format.append(int(octave))

            new_tuning_name = self.tuning_namer_box.get()

            if new_tuning_name =="":
                mb.showerror("Error","No Name Entered", parent= self)

            elif self.is_too_long(new_tuning_name) == True:
                mb.showerror("Error","Tuning Name is too Long. Tuning Names Must Not be Over 20 characters.")

            elif self.new_tuning == True:

                if self.is_name_repeat(new_tuning_name) == False:
            
                    print("Creating New Tuning")
                    new_tuning_name = self.tuning_namer_box.get()
                    self.database.insert_new_tuning(tuning_values=tuning_proper_format, tuning_name = new_tuning_name)
                
                else:
                    
                    mb.showerror("Error",f"A Tuning is Already Named {new_tuning_name} Please Try Again")

            elif self.new_tuning == False:

                self.database.edit_tuning(tuning_proper_format, new_tuning_name, original_name=self.original_tuning_name)


        else:

            mb.showerror("Error", "Not All Strings Have Been Assigned a Note")
        
        self.update_database_list()
                

    def delete_tuning(self):
        
        name_index=self.tunings_list.curselection()
        if name_index:
            name_index = name_index[0]
            tuning_name= self.tunings_list.get(name_index)
            double_check=mb.askquestion(f"Delete {tuning_name}?","Are Your sure?")
            if double_check == "yes":
                self.database.delete_tuning(tuning_name)
                self.update_database_list()


    def on_show(self):
        pass

    def on_hide(self):
        self.database.close_connection()

    def update_database_list(self):

        self.tunings_list.delete(0,tk.END)
        tuning_name_list=self.database.retrieve_database_collum("Tuning_name")
        for names in tuning_name_list:
            self.tunings_list.insert(tk.END,names)

    
    def is_name_repeat(self,new_tuning_name):

        current_name_list = self.database.retrieve_database_collum("Tuning_name")
        for name in current_name_list:
            if name == new_tuning_name:
                return True
        return False


    def is_too_long(self,new_tuning_name):

        if len(new_tuning_name) >21:
            return True
        else:
            return False
    








class Edit_or_choose_tuning(tk.Frame,general_methods):


    def __init__(self,parent,controller):
        super().__init__(parent, bg= "lightblue")
        self.controller =controller


        self.edit_button = tk.Button(self,
                                text="Edit or Add New Tuning",
                                font=("arial",20),
                                 command=self.to_tuning_editor)
    
        self.choose_button = tk.Button(self,
                                       text="Choose Tuning",
                                       font=("arial",20),
                                       command=self.to_tuning_list)
        
        self.edit_button.pack(side="left",padx=2,expand=True)
        self.choose_button.pack(side="right",padx=2,expand=True)


    def to_tuning_editor(self):

        self.controller.show_frame(Tuning_editor)
    
    
    def to_tuning_list(self):

        self.controller.show_frame(Tuning_list)



class Tuning_list(tk.Frame,general_methods):
    
    def __init__(self,parent,controller,chosen_tuning_name):

        super().__init__(parent,bg="lightblue")
        self.database=Database()
        self.controller =controller
        self.__chosen_tuning=""
        self.current_tuning=None
        try:
            notes, octaves=self.database.retrive_tuning(chosen_tuning_name)
        except:
            self.current_tuning=None
        
        if self.current_tuning != None:
            for i in range(0,len(notes)):
                self.current_tuning +=f"{notes[i]} {octaves[i]}, "
        

        main_menu_button = tk.Button(self,
                                      text= "Back to Main Menu",
                                      font=("arial",20),
                                      command=lambda: self.to_main_menu(self.__chosen_tuning,container=parent))
        
        self.tunings_list= tk.Listbox(self,
                                selectmode=tk.SINGLE,
                                font=("arial",18),
                                width=30
                                ) 

        self.tunings_list.pack(side="left",padx=30,expand=False,fill="y",pady=20)
        
        main_menu_button.pack(side="bottom",pady=30)

        self.tuning_name_list=self.database.retrieve_database_collum("Tuning_name")
        for names in self.tuning_name_list:
            self.tunings_list.insert(tk.END,names)

        self.current_tuning_display = tk.Label(self,
                                    text = self.current_tuning,
                                    width =27,
                                    height = 2,
                                    font = ("arial",20),
                                    bg = "white"
                                    )
        
        self.current_tuning_display.pack(side="top",pady=(50,0))

        self.current_tuning_name_label=tk.Label(self,
                                           text= chosen_tuning_name,
                                           font=("arial",16),
                                           background="lightblue")

        self.current_tuning_name_label.pack(side="top",padx=5)

        confirm_choice_button=tk.Button(self,
                                        text="Confirm Choice",
                                        command=self.confirm_choice,
                                        font=("arial",18)
                                        )
        
        confirm_choice_button.pack(side="top",expand=True,pady=(40,0))



    def confirm_choice (self):
        
        tuning_values=""
        name_index=self.tunings_list.curselection()
        self.__chosen_tuning= self.tunings_list.get(name_index)
        notes, octaves=self.database.retrive_tuning(self.__chosen_tuning)
        for i in range (0,len(notes)):
            tuning_values+=(f"{notes[i]} {octaves[i]}, ")

        self.current_tuning_display.config(text="")
        self.current_tuning_display.config(text=tuning_values)
        self.current_tuning_name_label.config(text=self.__chosen_tuning)
        self.send_tuning()


    def to_main_menu(self,chosen_tuning,container):
        
        self.controller.show_frame(main_menu)



    def on_show (self):
        
        self.tunings_list.delete(0,tk.END)
        tuning_name_list=self.database.retrieve_database_collum("Tuning_name")
        for names in tuning_name_list:
            self.tunings_list.insert(tk.END,names)
        
        if len(tuning_name_list) == 0:
            self.current_tuning_name_label.config(text="")
            self.current_tuning_display.config(text="No Tuning Chosen")
            self.__chosen_tuning=None
            self.send_tuning()


    def send_tuning (self):

        self.controller.frames[main_menu].recieve_tuning(self.__chosen_tuning)
        self.controller.frames[Tuning_interface].recieve_tuning(self.__chosen_tuning)


    def does_current_tuning_exist(self):

        for i in self.tuning_name_list:
             
             if i == self.current_tuning:
                 return False
        
        return True

    