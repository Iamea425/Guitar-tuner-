import numpy as np
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
    
        #takes recording info from audio class 
        self.__stream=self.audio_import.data_extract()
        




    def getting_pitch_extraction(self):#needs to be looped 

        chunks=self.__stream.read(self.__chunk)
        self.data = np.frombuffer(chunks,dtype=np.float32)#turns the raw data into float32 format
        
        # self.data=self.increase_gain()
        self.data=np.reshape(self.data,(-1,))
        self.data=self.harmonic_filter()
        self.data=np.array(self.data,np.float32)


        final_data_Hz=self.DFT_analyser()
        print(final_data_Hz)


        return final_data_Hz#final output



    def stop(self):
        self.audio_import.end_recording()
    


    def increase_gain (self):
        return (np.clip(self.data*1.25,-1.0,1.0))
    


    def harmonic_filter(self, cutoff=1000, fs=44100, order=5):
        nyquist = 0.5 * fs  # nyquist frequency (half of sampling rate)
        normal_cutoff = cutoff / nyquist  # normalize cutoff frequency

        
        b, a = butter(order, normal_cutoff, btype='low', analog=False)

        # Apply the filter to the audio data
        filtered_data = filtfilt(b, a, self.data)
        return filtered_data
    


    def DFT_analyser(self, harmonics=5, fmin=50, fmax=1000):
        
        FFT_SIZE = 8192 
        windowed = self.data[:FFT_SIZE] * np.hamming(FFT_SIZE)
        
        # FFT magnitude spectrum
        spectrum = np.abs(np.fft.rfft(windowed, n=65536 )) #zero pads the FFT size to increase percieved resolution
        freqs = np.fft.rfftfreq(65536, 1/self.__rate)
        
        # Initialize HPS spectrum
        hps_spec = spectrum.copy()
        
        # Multiply downsampled spectra
        for h in range(2, harmonics+1):
            downsampled = spectrum[::h]
            hps_spec[:len(downsampled)] *= downsampled
        
        # Restrict search to expected note range
        mask = (freqs >= fmin) & (freqs <= fmax)
        search_spec = hps_spec[mask]
        search_freqs = freqs[mask]

        if len(search_spec) == 0:
            return 0  # No frequencies in the specified range
        
         # Find rough peak in restricted range
        rough_idx = np.argmax(search_spec)
        

        # fall back if interpolation fails
        global_idx = np.where(mask)[0][rough_idx]

        # quadraric interpolation for better accuracy
        if 1 <= global_idx < len(hps_spec)-1:
            alpha, beta, gamma = hps_spec[global_idx-1], hps_spec[global_idx],hps_spec[global_idx+1]
            offset = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
            peak_index = global_idx + offset
            fundamental_frequency = freqs[0] + peak_index * (freqs[1] - freqs[0])

        # remove pitches outside expected range
        if fundamental_frequency <50 or fundamental_frequency > 1000:
            fundamental_frequency=0
        
        return fundamental_frequency

    
    


