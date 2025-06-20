from tkinter import HORIZONTAL
import tkinter as tk
from tkinter.ttk import * 
from getting_pitch import Getting_pitch


class main_menu(tk.Tk):



    def __init__(self):

        self.root=tk.Tk() 

        self.root.geometry("1600x900")
        tune_button=Button(self.root, text="Tune",width=25,command=self.open_tuning_interface)
        tune_button.pack()
        self.root.mainloop()



    def open_tuning_interface(self):
        instance=Tuning_interface()
        self.root.destroy
        instance.mainloop



class Tuning_interface(tk.Tk):



    def __init__(self):

        self.root=tk.Tk()

        self.audio_import=Getting_pitch()
    
        self.bar=Progressbar(self.root,
                        orient=HORIZONTAL,
                        length=1000,
                        mode="indeterminate",
                        
        )
        self.bar["value"]=0
        self.audio_import.getting_pitch_start()
        self.bar.pack(pady=100)
        self.root.after(100, self.update_bar)
        self.root.mainloop()



    def update_bar(self):
        pitch =self.audio_import.getting_pitch_extraction()
        print(pitch)
        if pitch==0:
            pass
        else:
            if pitch>100:
                pitch=100

            self.bar["value"]=pitch
            self.root.update()
        self.root.after(100, self.update_bar)



test=main_menu()
test.mainloop