import pandas as pd
import numpy as np
from file_processing import FileProcessing

"""This files contains all the functions to analysis EPIS results"""
class EPISResults:
    """This class calculates the result of EPIS"""
    def __init__(self, file_names, file_type, sinefit):
        self.length = len(file_names)
        freqs, pins, pouts, voltages, p_pipes = [], [], [], [], []
        for file_name in file_names:
            single_frequency_data = FileProcessing(file_name, file_type, sinefit)
            freq = single_frequency_data.find_base_frequency()
            p_pipe = single_frequency_data.find_fft_max('pressure_cathode_inlet')
            pin = single_frequency_data.find_fft_max('pressure_cathode_inlet_spare')
            pout = single_frequency_data.find_fft_max('pressure_cathode_outlet')
            # Set voltages to mV
            voltage = single_frequency_data.find_fft_max('voltage') * 1000
            p_pipes.append(p_pipe)
            pins.append(pin)
            pouts.append(pout)
            freqs.append(freq)
            voltages.append(voltage)
        self.frequency = freqs
        results_dict = {'Frequency': freqs, 'Pressure Inlet': pins, 'Pressure Outlet': pouts, 'Voltage': voltages, 'Pressure Pipe': p_pipes}
        self.results = pd.DataFrame(data=results_dict)

    def convert_complex_numbers(self, tag):
        """Seperate the real part and the imaginary part of a complex number"""
        real, img, mag = [], [], []
        for i in range(0, self.length):
            value = self.results.at[i, tag]
            mag.append(abs(value))
            real.append(value.real)
            img.append(value.imag)
        complex_dict = {tag + ' Real': real, tag + ' Imaginary': img, tag + ' Magnitude': mag}
        return complex_dict

    def export_results_to_csv(self, location):
        """Export the results to a .csv file"""
        pressure_inlet_dict = self.convert_complex_numbers('Pressure Inlet')
        pressure_outlet_dict = self.convert_complex_numbers('Pressure Outlet')
        voltage_dict = self.convert_complex_numbers('Voltage')
        new_results_dict = {'Frequency': self.frequency} | pressure_inlet_dict | pressure_outlet_dict | voltage_dict
        new_results = pd.DataFrame(data=new_results_dict)      
        new_results.to_csv(location, index=False)
        print('Results are saved to: '+ location)

    def get_zeta_from_results(self, output_tag):
        input = np.array(self.results['Pressure Outlet'])
        output = np.array(self.results[output_tag])
        zeta = output / input
        return zeta

# Independent epis functions, not included in the Result class
def get_frequency_array(file_names, file_type):
    freqs = []
    for file_name in file_names:
        single_frequency_data = FileProcessing(file_name, file_type)
        freq = single_frequency_data.find_base_frequency()
        freqs.append(freq)
    return freqs

def get_variable_array(file_names, file_type, tag):
    variables = []
    for file_name in file_names:
        single_frequency_data = FileProcessing(file_name, file_type)
        variable = single_frequency_data.find_fft_max(tag)
        variables.append(variable)
    return variables

def get_zeta_array(file_names, file_type, tag):
    zetas = []
    for file_name in file_names:
        single_frequency_data = FileProcessing(file_name, file_type)
        pressure = single_frequency_data.find_fft_max('pressure_cathode_outlet')
        output = single_frequency_data.find_fft_max(tag)
        zeta = output / pressure
        zetas.append(zeta)
    return zetas

def get_epis_results(file_names, file_type):
    """This function is now integrated in the init function. Also can be called seperately"""
    freqs, pins, pouts, voltages = [], [], [], []
    for file_name in file_names:
        single_frequency_data = FileProcessing(file_name, file_type)
        freq = single_frequency_data.find_base_frequency()
        pin = single_frequency_data.find_fft_max('pressure_cathode_inlet_spare')
        pout = single_frequency_data.find_fft_max('pressure_cathode_outlet')
        # Set voltages to mV
        voltage = single_frequency_data.find_fft_max('voltage') * 1000
        pins.append(pin)
        pouts.append(pout)
        freqs.append(freq)
        voltages.append(voltage)
    results_dict = {'Frequency': freqs, 'Pressure Inlet': pins, 'Pressure Outlet': pouts, 'Voltage': voltages}
    results = pd.DataFrame(data=results_dict)
    return results

def get_time_domain_results(file_names, file_type):
    """This function is used to get time domain results (DC values, amplitude, etc.)"""
    freqs, pin_amps, pin_dcs, pout_amps, pout_dcs, voltage_amps, voltage_dcs, ppipe_dcs = [], [], [], [], [], [], [], []
    for file_name in file_names:
        single_frequency_data = FileProcessing(file_name, file_type)
        freq = single_frequency_data.find_base_frequency()
        pin_amp = single_frequency_data.find_amplitude('pressure_cathode_inlet_spare')
        pout_amp = single_frequency_data.find_amplitude('pressure_cathode_outlet')
        voltage_amp = single_frequency_data.find_amplitude('voltage')
        ppipe_dc = single_frequency_data.read_dc_value('pressure_cathode_inlet')
        pin_dc = single_frequency_data.read_dc_value('pressure_cathode_inlet_spare')
        pout_dc = single_frequency_data.read_dc_value('pressure_cathode_outlet')
        #change for get flow rate
        voltage_dc = single_frequency_data.read_dc_value('total_cathode_stack_flow')
        pin_amps.append(pin_amp)
        pout_amps.append(pout_amp)
        voltage_amps.append(voltage_amp)
        pin_dcs.append(pin_dc)
        pout_dcs.append(pout_dc)
        ppipe_dcs.append(ppipe_dc)
        voltage_dcs.append(voltage_dc)
        freqs.append(freq)
    td_results_dict = {'Frequency': freqs, 'Pressure Inlet Amplitude': pin_amps, 'Pressure Outlet Amplitude': pout_amps, 'Voltage Amplitude': voltage_amps,  
        'Pressure Pipe DC': ppipe_dcs, 'Pressure Inlet DC': pin_dcs, 'Pressure Outlet DC': pout_dcs, 'Voltage DC': voltage_dcs}
    td_results = pd.DataFrame(data=td_results_dict)
    return td_results

def combine_time_domain_data_to_one(file_names, file_type):
    total_pin, total_pout, total_voltage = np.array([]), np.array([]), np.array([])
    for file_name in file_names:
        single_frequency_data = FileProcessing(file_name, file_type)
        pin = single_frequency_data.get_column('pressure_cathode_inlet_spare')
        pout = single_frequency_data.get_column('pressure_cathode_outlet')
        # Set voltages to mV
        voltage = single_frequency_data.get_column('voltage') * 1000
        total_pin = np.concatenate((total_pin, pin), axis=None)
        total_pout = np.concatenate((total_pout,pout))
        total_voltage = np.concatenate((total_voltage, voltage))
    all_data_dic = {'Inlet': total_pin, 'Outlet': total_pout, 'Voltage': total_voltage}
    all_data = pd.DataFrame(data=all_data_dic).reset_index()    
    return all_data


