import pyaudio 
import time 

class recording:
    

    def __init__(self):
        #setting recording parameters
        self.__chunk=8192
        self.__format=pyaudio.paFloat32
        self.__channels=1
        self.__rate=44100
        #creating pyaudio object
        self.__input=pyaudio.PyAudio()


    def start_recording(self):

        self.__stream=self.__input.open(format=self.__format,
                            channels=self.__channels,
                            rate=self.__rate,
                            input=True,
                            frames_per_buffer=self.__chunk
        )
        print("recording started")
        time.sleep(1)

    def end_recording(self):

        self.__stream.stop_stream()
        self.__stream.close
        self.__input.close
        print ("recording ended")


    def parameter_extract(self):

        #must be assigned in exact order
        return self.__chunk,self.__format,self.__channels,self.__rate,self.__input
    
    
    def data_extract(self):
        return self.__stream
    

    


