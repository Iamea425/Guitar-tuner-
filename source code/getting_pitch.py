import numpy as np
from audio import recording
from scipy.signal import butter,filtfilt 
import math

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
        
        try:
            chunks=self.__stream.read(self.__chunk)
        except:
            return 0
        self.data = np.frombuffer(chunks,dtype=np.float32)#turns the raw data into float32 format
        
        # self.data=self.increase_gain()
        self.data=np.reshape(self.data,(-1,))

        self.data=np.array(self.data,np.float32)
        self.data = self.increase_gain()

        final_data_Hz=self.FT_analyser()


        return final_data_Hz#final output



    def stop(self):
        self.audio_import.end_recording()
    


    def increase_gain (self):
        return (np.clip(self.data*1.25,-1.0,1.0))
    
    


    def FT_analyser(self, harmonics=5, fmin=50, fmax=1000):
        
        FFT_SIZE = 8192 
        windowed = self.data[:FFT_SIZE] * np.hamming(FFT_SIZE)

        continue_analysis= self.check_for_signal(windowed)# stops random noise from being generated when no input is recieved 

        if continue_analysis == False:
            return 0
        
        # prepares the microphone input for the FT algorithm
        zero_padded_data = self.__zero_pad(windowed)
        full_fft = np.array(self.fourier_algorithm(zero_padded_data.tolist()), dtype = np.complex128)

        spectrum = np.abs(full_fft[:65536 // 2+1])
        
        freqs= np.arange(0, 65536 // 2+1) * (self.__rate / 65536)

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
        
         # Find rough estimate for fundomental frequency 
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
    

    def check_for_signal(self, windowed):

        signal_strength = np.sum(windowed ** 2)
        if signal_strength < 0.0001:
            return False
        else:
            return True
        


    def fourier_algorithm(self,signal):

        N = len(signal)
    
        # Base case: one value
        if N == 1:
            return signal
        
        # Ensure length is power of 2
        if N % 2 != 0:
            raise ValueError("Signal length must be a power of 2")
        
        # Split into even and odd samples
        even = self.fourier_algorithm(signal[0::2])
        odd = self.fourier_algorithm(signal[1::2])
        
        result = [0] * N
        
        for k in range(N // 2):
            
            angle = -2 * math.pi * k / N
            
            # Complex rotation factor
            twiddle = complex(math.cos(angle), math.sin(angle))
            
            t = twiddle * odd[k]
            
            result[k] = even[k] + t
            result[k + N//2] = even[k] - t
        
        return result
    
    

    def __zero_pad(self,data, pad_by =65536):
        
        if len(data)< pad_by:
            fft_in = np.pad(data, (0, pad_by - len(data)))
        else:
            fft_in = data[:pad_by]

        return fft_in