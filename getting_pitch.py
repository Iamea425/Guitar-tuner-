import numpy as np
import aubio
from audio import recording
from scipy.signal import butter,filtfilt

class Getting_pitch():

    def __init__(self):

        #creating audio class instance
        self.audio_import=recording()

        #getting parameters from the base audio class
        self.__chunk,self.__format,self.__channels,self.__rate,self.__input=self.audio_import.parameter_extract()

        self.__tolerance = 0.4
        self.__win_s = 16384 # fft size
        self.__hop_s = self.__chunk # hop size



    def getting_pitch_start(self):

        self.audio_import.start_recording()
        self.__pitch_o = aubio.pitch("mcomb", self.__win_s, self.__hop_s, self.__rate)
        self.__pitch_o.set_unit("midi")
        self.__pitch_o.set_tolerance(self.__tolerance)

        #takes recording info from audio class 
        self.__stream=self.audio_import.data_extract()
        




    def getting_pitch_extraction(self):#needs to be looped 

        chunks=self.__stream.read(self.__chunk)
        self.data = np.frombuffer(chunks,dtype=np.float32)#turns the raw data into float32 format
        self.data=self.increase_gain()
        self.data=np.reshape(self.data,(-1,))
        self.data=self.harmonic_filter()
        self.data=np.array(self.data,np.float32)
        final_data_Hz=self.DFT_analyser()
        final_data= 69 + 12 * np.log2(final_data_Hz / 440.0) if final_data_Hz > 0 else 0
        pitch=self.__pitch_o(self.data)[0]
        confidence=self.__pitch_o.get_confidence()
        
        self.value_with_confidence="{} / {}".format(pitch,confidence)


        return final_data_Hz



    def stop(self):
        self.audio_import.end_recording()
    


    def increase_gain (self):
        return (np.clip(self.data*2,-1.0,1.0))
    


    def harmonic_filter(self, cutoff=1000, fs=44100, order=5):
        nyquist = 0.5 * fs  # Nyquist frequency (half of sampling rate)
        normal_cutoff = cutoff / nyquist  # Normalize cutoff frequency

        
        b, a = butter(order, normal_cutoff, btype='low', analog=False)

        # Apply the filter to the audio data
        filtered_data = filtfilt(b, a, self.data)
        return filtered_data
    


    def DFT_analyser(self):

        fft_spectrum=np.fft.fft(self.data)
        harmonics= np.fft.fftfreq(len(self.data),d=1/self.__rate)#finds the harmonics

        peak_index=np.argmax(np.abs(fft_spectrum))#finds harmonic with highest amplitude

        fundomental_frequency= harmonics[peak_index]#gets corrosponding frequency

        return fundomental_frequency