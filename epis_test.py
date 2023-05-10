#This it the main body of the EPIS data processing
#Author: Qingxin Zhang
from read_directory import Directory
from analysis_functions import EPISResults
import analysis_functions as af
#import epis_plot as episplt

#Read the directory and specify the file type(i.e., csv or xlsx)
directory = Directory('W:/Qingxin Zhang/01 - FCDX EPIS/01 Data processing code/Sample files/EPIS0311')

#Get all the files inside the directory
file_names = directory.file_names
file_type = directory.data_type

results = af.combine_time_domain_data_to_one(file_names, file_type)
#results = EPISResults(file_names, file_type)
#results.export_results_to_csv('W:/Qingxin Zhang/01 - FCDX EPIS/01 Data processing code/Sample files/kajs.csv')

#zeta = af.get_zeta_from_results(results, 'Voltage')
#episplt.plot_nyquist(zeta)
#episplt.plot_bode_mag(zeta, results['Frequency'])

#for file_name in file_names:
#    """This is the loop which loops all the files inside the folder. Insert your command here"""
    
#print(single_frequency_data.get_frequencies())
#single_frequency_data.plot_frequency_domain_data('pressure_anode_outlet')

#print(voltages)
#print(zeta)
