from tkinter import HORIZONTAL
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import * 
from getting_pitch import Getting_pitch
from database import Database



class general_methods():

    def __init__(self):
        self.chosen_tuning_name = ""
    

    def start_up (self):
        try:
            database_object= Database()
            tuning_names=database_object.retrieve_database_collum("Tuning_name")
            self.chosen_tuning_name = str(tuning_names[0])
        except:
            self.chosen_tuning_name =None
        print(self.chosen_tuning_name)


class App_interface(tk.Tk,general_methods):

    def __init__(self):
        self.start_up()
        super().__init__()
        self.title("Guitar Tuner")
        self.center_screen()

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        
        # Configure grid weights so frames expand to fill screen
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None

        self.frames={}

        for Page in (main_menu, Tuning_editor, Tuning_interface, Edit_or_choose_tuning, Tuning_list):
            if Page == main_menu:
                frame = Page(controller=self, parent=container)
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



    def __init__(self,parent, controller):
        super().__init__(parent, bg="lightblue")

        self.controller =controller
        self.current_tuning=""
        self.database = Database()


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
        print("this is running")
        self.current_tuning=""
        self.database.check_exist()
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
            self.current_tuning = "No tuning selected"
        print(self.current_tuning)
        
        self.current_tuning_display.configure(text=self.current_tuning)


    def on_hide(self):
        self.database.close_connection()






class Tuning_interface(tk.Frame,general_methods):



    def __init__(self,parent,controller):
        super().__init__(parent, bg="lightblue")

        self.controller =controller
        self.audio_import=Getting_pitch()
        self.pitch = 0
        self.update_job = None  # Initialize update_job
    
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

        
        back_to_main_menu.pack(expand=True,side="bottom")

        self.bar["value"]=0

    def on_show(self):
        self.audio_import.getting_pitch_start()
        self.bar.pack(pady=100,side="top")
        self.update_job = self.after(100, self.update_bar)

        

        

    def update_bar(self):

        self.pitch =self.audio_import.getting_pitch_extraction()
        print(self.pitch)
        self.update_hertz_value()
        
        if self.pitch==0:
            pass
        else:
            if self.pitch>100:
                self.pitch=100

            self.bar["value"]=self.pitch
            self.update()
        # Only schedule the next update if the widget still exists
        if self.winfo_exists():
            self.update_job = self.after(300, self.update_bar)

    def update_hertz_value(self):

        self.hertz_value.config(text = f"{round(self.pitch, 1)} Hz")

    def return_to_main_menu(self):
        # Cancel any pending after() calls
        self.controller.show_frame(main_menu)


    def on_hide(self):
        self.audio_import.stop()









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


    def create_new_tuning(self):
        
        self.tuning_namer_box.delete(0,tk.END) # clears the naming box for new tuning
        self.new_tuning=True
        self.final_tuning= {1:None,2:None,3:None,4:None,5:None,6:None}
        self.final_tuning_display = (", ".join(str(v) for v in self.final_tuning.values()))
        self.update_final_tuning()
        

    
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
                print("Error: No Tuning Name Entered")#to be replaced with proper pop up error message and to include other invalid name inputs

            elif self.new_tuning == True:
            
                print("Creating New Tuning")
                new_tuning_name = self.tuning_namer_box.get()
                self.database.insert_new_tuning(tuning_values=tuning_proper_format, tuning_name = new_tuning_name)

            elif self.new_tuning == False:

                self.database.edit_tuning(tuning_proper_format, new_tuning_name, original_name=self.original_tuning_name)


        else:
            print("Error: Not all strings have been assigned a note")#to be replaced with proper pop up error message
                

    def delete_tuning(self):
        pass

    def on_show(self):
        pass

    def on_hide(self):
        self.database.close_connection()



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
    
    def __init__(self,parent,controller):
        super().__init__(parent,bg="lightblue")
        self.controller =controller


