import struct
import io
import numpy as np
import shutil
import sys

"""
Converts the floats you give it into a binary line
*args -> pass in as many floats as you want

Example:
dec_to_bin(-8.5, 54.5486, -543, 64424)

To pass in a list:
my_list = [654, 14239.68, -68433, -12.221]
dec_to_bin(*my_list)
"""
def dec_to_bin(*args):
    return struct.pack(len(args) * "f", *args)

"""
Converts a binary line into the corresponding floats
byte -> the bytes object to unpack into floats
"""
def bin_to_dec(byte):
    return struct.unpack(int(len(byte) / 4) * "f", byte)

"""
Converts a binary file into the corresponding floats
buffer -> the binary data
numbers_per_line -> how many numbers there are in the line
number_of_lines -> how many lines there are

Returns 2D list, each list is a list containing the floats for the line
"""
def read_data(buffer, numbers_per_line, number_of_lines):
    data = []
    for line in range(number_of_lines):
        data.append(struct.unpack_from(numbers_per_line * "f",
                                       buffer,
                                       line * numbers_per_line * 4))
    return data

def convert_numpy_array(numpy_array):
    compressed_array = io.BytesIO()    # np.savez_compressed() requires a file-like object to write to
    np.savez_compressed(compressed_array, numpy_array)
    return compressed_array

def read_data(file, processPair):
    while True:
        chunk = file.read(4)
        if chunk == '':
            break
        input_array = get_array(file, chunk)
        chunk = file.read(4)
        if chunk == '':
            break
        output_array = get_array(file, chunk)
        processPair(input_array, output_array)

def get_array(file, chunk):
    startingByte = struct.unpack('i', chunk)[0]
    numpyBytes = file.read(startingByte)
    fakeFile = io.BytesIO(numpyBytes)
    result = np.load(fakeFile)
    return result[result.files[0]]

def default_process_pair(input_array, output_array):
    print(input_array)
    print(output_array)

if __name__ == '__main__':
    file = open('training\\1511676262748-30\\SaltieRl(2).txt', 'r+b')
    print(file)
    read_data(file, default_process_pair)
