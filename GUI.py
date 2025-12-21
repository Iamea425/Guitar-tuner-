from tkinter import HORIZONTAL
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import * 
from getting_pitch import Getting_pitch
from database import Database


class main_menu(tk.Tk):



    def __init__(self,tuning_name):
        super().__init__()

        
        self.title("Guitar Tuner")
        self.geometry("1600x900")
        self.configure(bg="lightblue")
        self.database = Database()
        self.database.check_exist()
        self.current_tuning = self.database.retrive_tuning(tuning_name)
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
        
        current_tuning_display = tk.Label(header_frame,
                                          text = self.current_tuning,
                                          width =15,
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
        current_tuning_display.pack(side = "top", expand = True, padx=2 )
        tuning_label.pack(side ="top",expand=True, padx=2)
        database_button.pack(expand=True,side="left",padx=2)
        tune_button.pack(expand=True,side="right",padx=1,pady=5)

    
        self.mainloop()



    def open_tuning_interface(self):
        self.destroy()
        instance=Tuning_interface()
        instance.mainloop()

    def open_database_menu(self):
        self.destroy()
        instance=Edit_or_choose_tuning()
        instance.mainloop()



class Tuning_interface(tk.Tk):



    def __init__(self):
        

        self.root=tk.Tk()
        self.root.geometry("1600x900")
        self.root.configure(bg="lightblue")
        self.audio_import=Getting_pitch()
        self.pitch = 0
    
        self.bar=Progressbar(self.root,
                        orient=HORIZONTAL,
                        length=1000,
                        mode="indeterminate",)
        
        back_to_main_menu=tk.Button(self.root,
                                    width=20,
                                    height=3,
                                    font=("arial",14),
                                    text="Back To Main Menu",
                                    command=self.return_to_main_menu)
        
        self.hertz_value = tk.Label(self.root,
                               text = f"{self.pitch} Hz",
                               font = ("arial",24,"bold"),
                               bg = "lightblue",
                               fg = "red",
                               width = 15,
                               
                            )
        self.hertz_value.pack(pady=10)

        
        back_to_main_menu.pack(expand=True,side="bottom")

        self.bar["value"]=0
        self.audio_import.getting_pitch_start()
        self.bar.pack(pady=100,side="top")
        self.root.after(100, self.update_bar)
        self.root.mainloop()

        

        

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
            self.root.update()
        self.root.after(300, self.update_bar)

    def update_hertz_value(self):

        self.hertz_value.config(text = f"{round(self.pitch, 2)} Hz")

    def return_to_main_menu(self):

        self.root.destroy()
        instance = main_menu()
        instance.mainloop()






class Tuning_editor (tk.Tk):


    def __init__(self):
        super().__init__()

        database=Database()
        self.title("Tuning Selector")
        self.geometry("1600x900")
        self.configure(bg="lightblue")
        note_list=[]
        self.final_tuning= {1:None,2:None,3:None,4:None,5:None,6:None}
        self.final_tuning_display = (", ".join(str(v) for v in self.final_tuning.values())) # formats the dictionary into a printable list

        notes=database.value_retrieval() # creates all combonations of note and octave
        for octaves in range (1,5):
            for note in notes:
                note_list.append(f"{note} {octaves}" )

        top_container = tk.Frame(self, bg="lightblue")
        top_container.pack(pady=20, padx=15, anchor="n", fill="x")


        choice_frame = tk.Frame(self, bg="lightblue") # groups the comboboxes together 
        choice_frame.pack(pady=20,side="right",padx=20)

        name_input_frame = tk.Frame(self, bg = "lightblue" )
        name_input_frame.pack(pady = 20, padx = 20 ,anchor = "center",fill="x"  )

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
            self.note_choice.pack(side="left",padx=10)
            
            conformation = tk.Button(individual_frame,
                                     font=("arial",12),
                                     text="Confirm",
                                     command=lambda idx=i,
                                     c=self.note_choice: self.confirm_choice(idx, c)
                                     )
            
            conformation.pack(expand=True, side="left", padx=10)

        self.tuning_display = tk.Label(top_container,           # displays the current selected notes
                                        font = ("arial",18),
                                         text = f"{self.final_tuning_display}",
                                         height= 1,
                                         width = 30
                                         )
        self.tuning_display.pack(side = "top",anchor= "n",pady=20,padx=1)

        back_to_main_menu=tk.Button(self,
                                    width=20,
                                    height=3,
                                    font=("arial",14),
                                    text="Back To Main Menu",
                                    command=self.return_to_main_menu
                                    
        )
        back_to_main_menu.pack(side = "bottom", pady=30)

        tuning_namer_box = tk.Entry(name_input_frame, font=("arial",18), width = 30)
        tuning_namer_box.pack(pady = 10,side="bottom",padx=50)

        tuning_namer_label = tk.Label(name_input_frame,
                                      font=("arial",14),
                                      text="Tuning Name",
                                      bg = "lightblue",
                                      width = 30 )
        tuning_namer_label.pack(side="top")


    def return_to_main_menu(self):
        self.destroy()
        instance = main_menu(tuning_name="standard")
        instance.mainloop()


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




class Edit_or_choose_tuning(tk.Tk):


    def __init__(self):
        super().__init__()
        self.title("Edit or Choose Tuning")
        self.geometry("1600x900")
        self.configure(bg="lightblue")

        self.edit_button = tk.Button(self,
                                text="Edit or Add New Tuning",
                                font=("arial",20),
                                 command=self.to_tuning_editor
                                )
    
        self.choose_button = tk.Button(self,
                                       text="Choose Tuning",
                                       font=("arial",20),
                                       command=self.to_tuning_list)
        
        self.edit_button.pack(side="left",padx=2,expand=True)
        self.choose_button.pack(side="right",padx=2,expand=True)


    def to_tuning_editor(self):

        self.destroy()
        instance=Tuning_editor()
        instance.mainloop()
    
    
    def to_tuning_list(self):

        self.destroy()
        instance=Tuning_list()
        instance.mainloop()




class Tuning_list(tk.Tk):
    
    def __init__(self):
        super().__init__()
        self.title("Choose Tuning")
        self.geometry("1600x900")
        self.configure(bg="lightblue")


test=main_menu(tuning_name="standard")
test.mainloop