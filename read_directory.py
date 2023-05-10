#from pathlib import Path
import os

class Directory:
    """This is the class about the directory that contains EPIS data"""
    def __init__(self, directory):
        self.file_names = self.get_file_names(directory)
        self.data_type = os.path.splitext(self.file_names[0])[-1].lower()
    # def __init__(self, directory, data_type):
    #     """This class needs to specify the directory and the data type"""
    #     self.directory = Path(directory)
    #     self.data_type = data_type
    #     #self.path = Path(self.directory)        
        self.number_of_files = len(self.file_names)

    def get_file_names(self, directory):
        """Output all the required files to an array"""
        all_files = os.listdir(directory)
        file_names = []
        for file in all_files:
           file_name = directory + "\\" + file
    #     for file in self.directory.rglob('*.' + self.data_type):
    #         file_name = directory + "\\" + file.name
           file_names.append(file_name)
        return file_names
        
