import pandas as pd
from numpy.fft import fft, fftfreq
import numpy as np
import matplotlib.pyplot as plt

class FileProcessing:
    """This class process file, extract the tag infomation, and remove the extra spaces, and do a frequency domain analysis"""
    def __init__(self, filename, type, sinefit=False):
        if type == '.csv':
            self.file = pd.read_csv(filename, encoding='latin', low_memory=False)
        if type == '.xlsx':
            self.file = pd.read_excel(filename, encoding='latin')
        self.header_row_number = self.find_header_row_number()
        self.tags = self.get_tags()
        self.remove_rows()
        self.remove_abnormal_peak('voltage')
        self.remove_abnormal_peak('pressure_cathode_inlet_spare')
        self.remove_abnormal_peak('pressure_cathode_outlet')
        self.remove_dc_components()
        if sinefit == True:
            self.remove_abnormal_peak('voltage')
            self.remove_abnormal_peak('pressure_cathode_inlet_spare')
            self.remove_abnormal_peak('pressure_cathode_outlet')
            self.sine_fit('voltage', self.find_base_frequency())
            self.sine_fit('pressure_cathode_inlet_spare', self.find_base_frequency())
            self.sine_fit('pressure_cathode_outlet', self.find_base_frequency())

    def find_header_row_number(self):
        """This function finds the header row and return the index"""
        for row in self.file.index:
            if self.file.loc[row, self.file.columns[0]] == 'Time Stamp':
                return row
        print("Cannot find header row")

    def get_tags(self):
        """This function gets the tags stored in the datalogger and return a list"""
        tags = []
        header_row = self.file.loc[self.header_row_number]
        for tag in header_row:
            tags.append(tag)
        return tags

    def remove_rows(self):
        """This function removes all the unnecessary rows and reset the header"""
        self.file = self.file.set_axis(self.tags, axis='columns')
        self.file = self.file.drop(range(0, self.header_row_number + 1))
        self.file = self.file.reset_index(drop=True)

    def get_column(self, tag):
        """This function gets the specific column of a tag"""  
        column = np.array(list(map(float, self.file.loc[:, tag])))
        return column

    def read_dc_value(self, tag):
        """This function gets the DC value of a tag"""
        dc_value = np.average(self.get_column(tag))
        return dc_value

    def find_amplitude(self, tag):
        """This function outputs the amplitude of the tag"""
        amplitude = np.sqrt(2) * np.std(self.get_column(tag))
        return amplitude

    def get_sampling_rate(self):
        """This function outputs the sampling rate of the datalogger"""
        time_interval = float(self.file.loc[1, 'Elapsed Time']) - float(self.file.loc[0, 'Elapsed Time'])
        return time_interval

    def do_fft(self, tag):
        """This function keeps the first half of the fft results to return a single-sided fft"""
        double_fft_results = fft((self.get_column(tag) - self.read_dc_value(tag)))
        half_fft_length = int(0.5 * len(double_fft_results))
        fft_results = double_fft_results[: half_fft_length]
        return fft_results

    def get_frequencies(self):
        """This function only keeps the positive frequencies"""
        full_freqs = fftfreq(len(self.get_column('Elapsed Time')), self.get_sampling_rate())
        half_freq_length = int(0.5 * len(full_freqs))
        freqs = full_freqs[: half_freq_length]
        return freqs

    def find_peak_position(self):
        """This function finds the input signal peak position and return the index"""
        pout_fft = self.do_fft('pressure_cathode_outlet')
        pout_fft_abs = abs(pout_fft)
        peak_pos = np.argmax(pout_fft_abs)
        return peak_pos

    def check_peak_position(self, tag):
        """This is a boolean function to check if the input and output is at the same base frequency"""
        tag_fft = self.do_fft(tag)
        tag_fft_abs = abs(tag_fft)
        tag_peak_pos = np.argmax(tag_fft_abs)
        if tag_peak_pos == self.find_peak_position():
            return True
        else:
            return False

    def find_base_frequency(self):
        """This is the function to find the base frequency of the signal"""
        freqs = self.get_frequencies()
        base_frequency = freqs[self.find_peak_position()]
        return base_frequency

    def find_fft_max(self, tag):
        """This is the function that finds the peak of the fft signal"""
        signal = self.do_fft(tag)
        peak_value = signal[self.find_peak_position()]
        return peak_value

    def plot_time_domain_data(self, tag):
        plt.figure(figsize=(6,6))
        plt.plot(self.get_column('Elapsed Time'), self.get_column(tag))
        plt.show()

    def plot_frequency_domain_data(self, tag):
        plt.figure(figsize=(6,6))
        plt.plot(self.get_frequencies(), abs(self.do_fft(tag)))
        plt.show()

    def sine_fit(self, tag, freq):
        """Sine curve fitting of a signal at a certain frequency"""
        tag_values = self.get_column(tag)
        tag_dc_value = self.read_dc_value(tag)
        tag_amplitude = self.find_amplitude(tag)
        times =  self.get_column('Elapsed Time')
        sampling_rate = self.get_sampling_rate()
        period_time = 1 / freq
        zero_delay_peak_time = period_time / 4
        period_points = int(period_time / sampling_rate)
        first_period = tag_values[0 : period_points]
        max_value = max(first_period)
        for index in range(2, period_points):
            tag_reading = tag_values[index]
            check_peak = tag_reading - max_value
            if check_peak == 0:
                after_peak = tag_values[index + 1] - tag_values[index]
                before_peak = tag_values[index] - tag_values[index - 1]
                if before_peak >= 0 and after_peak < 0:
                    peak_time = times[index]   
                    time_delay = zero_delay_peak_time - peak_time
                    break
        sine_fits = []
        for time in times:
            sine_fit = tag_amplitude * np.sin(2 * np.pi * freq * (time + time_delay))
            fit_value =tag_dc_value + sine_fit
            sine_fits.append(fit_value)
        self.file.loc[:, tag] = sine_fits
        #return sine_fits

    def find_abnormal_peak_exist(self, tag):
        """Find if the data contains a abnormal peak caused by water droplets"""
        tag_values = self.get_column(tag)
        values, counts = np.unique(tag_values, return_counts=True)
        average_value = np.average(tag_values)
        min_value = np.amin(values)
        max_value = np.amax(values)
        left_difference = average_value - min_value
        right_differnce = max_value - average_value
        difference_ratio = right_differnce/left_difference
        if counts[-1] == 1:
            if difference_ratio > 3:
                print('There is possibly a abnormal peak')
                print('The peak was found at %f'%max_value)
                return True
        return False

    def remove_abnormal_peak(self, tag):
        """This is the function that removes the abnormal peak from the signal"""
        if self.find_abnormal_peak_exist(tag):
            tag_values = self.get_column(tag)
            peak_position = np.argmax(tag_values)
            left_boundary, right_boundary = 0, 0
            for index in range(0, 1000):
                left_index = peak_position - index
                right_index = peak_position + index
                left_difference = tag_values[left_index] - tag_values[left_index - 1]
                right_difference = tag_values[right_index] - tag_values[right_index + 1]
                if left_difference < 0:
                    left_boundary = left_index
                if right_difference < 0:
                    right_boundary = right_index
                if left_boundary != 0 and right_boundary !=0:
                    break
            value_difference = tag_values[right_boundary] - tag_values[left_boundary]
            num_of_points = right_boundary - left_boundary
            ratio = value_difference/num_of_points
            starting_value = tag_values[left_boundary]
            for tag_value_index in range(left_boundary, right_boundary + 1):
                difference = tag_value_index - left_boundary
                new_value = difference * ratio + starting_value
                tag_values[tag_value_index] = new_value
            self.file.loc[:, tag] = tag_values

    def remove_dc_components(self):
        target_tags = ['pressure_cathode_inlet_spare', 'pressure_cathode_outlet', 'voltage', 'pressure_cathode_inlet']
        for tag in target_tags:
            tag_values = self.get_column(tag)
            dc_value = np.average(tag_values)
            new_tag_values = tag_values - dc_value
            self.file.loc[:, tag] = new_tag_values


            
         





     