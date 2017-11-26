import os
import binary_converter

def get_all_files():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    training_path = dir_path + '\\training'
    files = []
    for (dirpath, dirnames, filenames) in os.walk(training_path):
        for file in filenames:
            files.append(dirpath + '\\' + file)
    return files

def get_input_function():
    #fill your input function here!
    return binary_converter.default_process_pair

if __name__ == '__main__':
    files = get_all_files()
    input_function = get_input_function()
    for file in files:
        binary_converter.read_data(open(file, 'r+b'), input_function)
