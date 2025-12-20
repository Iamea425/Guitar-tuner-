import sqlite3
import os


class Database():

    def __init__(self):
         
         #set hardcoded possible databse entries 
         self.VALID_VALUES = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
         self.OCTIVES = [1,2,3,4]
         self.CORROSPONDING_FREQUENCIES = [55, 58.27, 61.74, 32.70, 34.65 ,65, 36.71 ,38.89 ,41.2 ,43.65 ,46.25 ,49 ,41.91]


    def connect_to_database(self):

        self.connect = sqlite3.connect("tuning_database.db")
        self.cursor = self.connect.cursor()

    
    def value_retrieval(self):

        return self.VALID_VALUES


    def configuration (self): # only runs on if database doesn't already exist
        
        table_creation = """
          CREATE TABLE TUNINGS (
          Tuning_name TEXT, 
          str_1_note TEXT, 
          str_1_oct INTEGER, 
          str_2_note TEXT, 
          str_2_oct INTEGER, 
          str_3_note TEXT, 
          str_3_oct INTEGER, 
          str_4_note TEXT, 
          str_4_oct INTEGER, 
          str_5_note TEXT, 
          str_5_oct INTEGER, 
          str_6_note TEXT, 
          str_6_oct INTEGER
          )
          """ 
        self.cursor.execute(table_creation)
        self.connect.commit()


        standard_tuning_insert = ("""INSERT INTO TUNINGS (
                                Tuning_name,
                                str_1_note, str_1_oct,
                                str_2_note, str_2_oct,
                                str_3_note, str_3_oct,
                                str_4_note, str_4_oct,
                                str_5_note, str_5_oct,
                                str_6_note, str_6_oct
                                  )
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""")
        standard_tunings_values = (
                                      "standard",
                                        "E", 4,
                                        "B", 3,
                                        "G", 3,
                                        "D", 3,
                                        "A", 2,
                                        "E", 2

                                  )
        self.cursor.execute(standard_tuning_insert,standard_tunings_values)
        self.connect.commit()
    

    def check_exist(self):

        does_not_exist= not os.path.exists("tuning_database.db")

        self.connect_to_database()

        if does_not_exist:

            print("Initialising database")
            self.configuration()
            print("Database initialised")

        else:
            print("Database initialised ")

       
        self.connect.close()

    def retrive_tuning (self,tuning_name):

        self.connect_to_database()

        generic_query = ("SELECT str_1_note,str_2_note,str_3_note,str_4_note,str_5_note,str_6_note FROM TUNINGS WHERE Tuning_name = ?")
        while True:
            try:
                self.cursor.execute(generic_query,(tuning_name,))
            except:
                return "database rerival error"
            
            row=self.cursor.fetchone()
            if row: #converts the tuple into a string
                return row
        
    
    def retrieve_database_collum(self,collumn_name):

        self.connect_to_database()

        query = f""" SELECT {collumn_name} FROM TUNINGS """
        while True:
            try:
                self.cursor.execute(query)
                values=self.cursor.fetchall()
            except:
                return ["database retrieval error"]  #theoretically not required as collumn_name is not user defined 
            
            results_list = [value[0] for value in values]

            self.connect.close()
            return results_list