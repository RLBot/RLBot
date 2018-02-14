import tkinter as tk


class ConfigObject:
    """

    """
    headers = None

    def __init__(self):
        self.headers = {}

    def __getitem__(self, x):
        return self.get_header(x)

    def add_header(self, header_name, header):
        self.headers[header_name] = header
        return header

    def add_header_name(self, header_name, is_indexed=False):
        header = ConfigHeader()
        header.is_indexed = is_indexed
        self.headers[header_name] = header
        return header

    def set_value(self, header_name, option, value):
        self.get_header(header_name).set_value(option, value)

    def get_header(self, header_name):
        if header_name in self.headers:
            return self.headers[header_name]
        return self.add_header_name(header_name)

    def get(self, section, option, index=None):
        return self.get_header(section).get(option, index=index)

    def getint(self, section, option, index=None):
        return self.get_header(section).getint(option, index=index)

    def getboolean(self, section, option, index=None):
        return self.get_header(section).getboolean(option, index=index)

    def getfloat(self, section, option, index=None):
        return self.get_header(section).getfloat(option, index=index)

    def parse_file(self, config_parser, max_index=None):
        """
        Parses the file internally setting values
        :param config_parser: an instance of configparser
        :return: None
        """
        for header_name in self.headers:
            header = self.headers[header_name]
            header.parse_file(config_parser[header_name], max_index=max_index)

    def reset(self):
        for header_name in self.headers:
            header = self.headers[header_name]
            header.reset()

    def __str__(self):
        for header_name in self.headers:
            return header_name + ':\n' + str(self.headers[header_name]) + '\n'


class ConfigHeader:
    values = None
    is_indexed = False  # if true then indexes will be applied to all values otherwise they will not be
    max_index = -1

    def __init__(self):
        self.values = {}

    def __getitem__(self, x):
        return self.values[x]

    def add_value(self, name, value_type, default=None, description=None, value=None):
        if description is None:
            description = name
        self.values[name] = ConfigValue(value_type, default=default, description=description, value=value)

    def set_value(self, option, value):
        self.values[option].value = value

    def get(self, option, index=None):
        return self.get_with_type(option, tk_type=tk.StringVar, index=index)

    def getint(self, option, index=None):
        return int(self.get_with_type(option, tk_type=tk.IntVar, index=index))

    def getboolean(self, option, index=None):
        return bool(self.get_with_type(option, tk_type=tk.BooleanVar, index=index))

    def getfloat(self, option, index=None):
        return float(self.get_with_type(option, tk_type=tk.DoubleVar, index=index))

    def get_with_type(self, option, tk_type, index=None):
        """
        Returns the default if value is none.  Grabs tk version if value is a tk value
        :param option: The string option that is being grabbed.
        :param tk_type:
        :param index: If this is an indexed option this will add the index to the end.
        :return:
        """

        return self.values[option].get_value(tk_type=tk_type, index=index)

    def parse_file(self, config_parser, max_index=None):
        if self.is_indexed and max_index is None:
            return  # if we do not know the index lets skip instead of crashing

        for value_name in self.values:
            self.values[value_name].parse_file(config_parser, value_name, max_index=max_index)

    def reset(self):
        for value_name in self.values:
            self.values[value_name].reset()

    def __str__(self):
        string = ''
        for value_name in self.values:
            string += '\t' + value_name + ':\n\t\t' + str(self.values[value_name]) + '\n'
        return string


class ConfigValue:
    def __init__(self, value_type, default=None, description="", value=None):
        self.type = value_type
        self.value = value
        self.default = default
        self.description = description

    def get_value(self, tk_type=tk.StringVar, index=None):
        """
        Returns the default if value is none.
        Grabs tk version if value is a tk value.
        :param tk_type:
        :return: A value.
        """

        if index is not None:
            value = self.value[index]
        else:
            value = self.value

        if value is None:
            return self.default

        return value.get() if isinstance(value, tk_type) \
            else value

    def __str__(self):
        return 'type: ' + str(type) + ' value: ' + str(self.get_value()) +\
               ' description: ' + str(self.description).replace('\n', '\n\t\t\t')

    def parse_file(self, config_parser, value_name, max_index=None):
        if max_index is None:
            self.value = config_parser[value_name]
        else:
            self.value = []
            for i in range(max_index):
                self.value.append(config_parser[value_name + '_' + str(i)])

    def reset(self):
        self.value = None
