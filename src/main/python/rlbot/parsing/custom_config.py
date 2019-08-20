from configparser import RawConfigParser
from pathlib import Path
from typing import Union
import re

import os


class ConfigObject:
    """
    Represents a parsed config file.
    Could be either of rlbot match or appearance config.
    The config schema is defined by calls to add_header().
    """

    def __init__(self):
        self.headers = {}
        self.raw_config_parser = None  # set by calling parse_file
        self.config_directory = None

    def __getitem__(self, x):
        return self.get_header(x)

    def add_header(self, header_name, header):
        """Adds the given header into this object with the name `header_name`"""
        self.headers[header_name] = header
        return header

    def add_header_name(self, header_name, is_indexed=False):
        """
        Adds a new header with the name header_name
        :param header_name: The name of the header as it would appear in the config
        :param is_indexed: Indicates that the header may contain special 'indexed' attributes, where a series of
        keys that differ only by a numeric suffix are used to represent an array. Example:
        thing_1 = x
        thing_2 = y
        :return: The newly created header.
        """
        header = ConfigHeader()
        header.is_indexed = is_indexed
        self.headers[header_name] = header
        return header

    def set_value(self, header_name, option, value, index=None):
        self.get_header(header_name).set_value(option, value, index)

    def get_header(self, header_name):
        """
        Returns a header with that name, creates it if it does not exist.
        """
        if header_name in self.headers:
            return self.headers[header_name]
        return self.add_header_name(header_name)

    def get(self, section, option, index=None):
        return self.get_header(section).get(option, index=index)

    def getpath(self, section, option, index=None):
        relative_path = self.get_header(section).get(option, index=index)
        if relative_path is None:
            return None
        return os.path.realpath(os.path.join(self.config_directory, relative_path))

    def getint(self, section, option, index=None):
        return self.get_header(section).getint(option, index=index)

    def getboolean(self, section, option, index=None):
        return self.get_header(section).getboolean(option, index=index)

    def getfloat(self, section, option, index=None):
        return self.get_header(section).getfloat(option, index=index)

    def init_indices(self, max_index):
        for header in self.headers.values():
            header.init_indices(max_index)

    def parse_file(self, config: Union[Path, str, RawConfigParser, 'ConfigObject'], max_index=None, config_directory=None):
        """
        Parses the file internally setting values
        :param config: an instance of RawConfigParser or a string to a .cfg file
        :param config_directory: The location of this config file on disk
        :return: None
        """
        self.config_directory = config_directory

        if isinstance(config, Path):
            config = str(config)

        if isinstance(config, str):
            if not os.path.isfile(config):
                raise FileNotFoundError(config)
            self.raw_config_parser = RawConfigParser()
            self.raw_config_parser.read(config, encoding='utf8')
            config = self.raw_config_parser
        elif isinstance(config, RawConfigParser):
            self.raw_config_parser = config
        elif not isinstance(config, ConfigObject):
            raise TypeError("The config should be a String, RawConfigParser of a ConfigObject")
        for header_name, header in self.headers.items():
            try:
                header.parse_file(config[header_name], max_index=max_index, config_directory=config_directory)
            except KeyError:
                pass  # skip this header as it does not exist
        return self

    def reset(self):
        for header_name in self.headers:
            header = self.headers[header_name]
            header.reset()

    def __str__(self):
        string = ''
        for header_name, header in self.headers.items():
            string += '[' + header_name + ']\n' + str(header) + '\n'
        return string

    def copy(self):
        new_object = ConfigObject()
        new_object.config_directory = self.config_directory
        for header_name, header in self.headers.items():
            new_object.add_header(header_name, header.copy())
        return new_object

    def has_section(self, header_name):
        """Returns true if the header exists"""
        return header_name in self.headers

    def get_raw_file(self):
        """Returns the raw file from the parser so it can be used to be parsed by other config objects."""
        return self.raw_config_parser


class ConfigHeader:

    def __init__(self):
        self.values = {}

        # Indicates that the header may contain special 'indexed' attributes, where a series of
        # keys that differ only by a numeric suffix are used to represent an array.
        self.is_indexed = False
        self.max_index = -1
        self.config_directory = None

    def __getitem__(self, x):
        return self.values[x]

    def add_value(self, name, value_type, default=None, description=None, value=None):
        """
        Adds a new value to this config header
        :param name: The name of the value as it would appear in a config file
        :param value_type:  The type of value: bool, str, int, float
        :param default: The value used when the config does not set any value.
        :param description: The human readable description of the value
        :param value: An optional value, if this header is indexed then the value needs to be a list.
        :return: an instance of itself so that you can chain adding values together.
        """
        if description is None:
            description = name
        if value is not None and self.is_indexed and not isinstance(value, list):
            raise Exception('Indexed values must be a list')
        self.values[name] = ConfigValue(value_type, default=default, description=description, value=value)
        return self

    def add_config_value(self, name, value):
        self.values[name] = value

    def set_value(self, option, value, index=None):
        """
        Sets the value on the given option.
        :param option: The name of the option as it appears in the config file
        :param value: The value that is being applied. If this section is indexed then the
        value must be a list (to be applied directly) or you must supply the index parameter,
        which will cause the value to be inserted into an existing list.
        :param index: If the attribute is indexed, we will use this index to insert
        the value you have supplied.
        :return: an instance of itself so that you can chain setting values together.
        """
        if self.is_indexed and index is None and not isinstance(value, list):
            raise TypeError("Value should be a list when not giving an index in an indexed header")
        self.values[option].set_value(value=value, index=index)
        return self

    def get(self, option, index=None):
        return self.values[option].get_value(index=index)

    def getpath(self, option, index=None):
        relative_path = self.values[option].get_value(index=index)
        if relative_path is None:
            return None
        return os.path.realpath(os.path.join(self.config_directory, relative_path))

    def getint(self, option, index=None):
        return int(self.values[option].get_value(index=index))

    def getboolean(self, option, index=None):
        return bool(self.values[option].get_value(index=index))

    def getfloat(self, option, index=None):
        return float(self.values[option].get_value(index=index))

    def init_indices(self, max_index):
        if not self.is_indexed:
            return
        self.max_index = max_index
        for value_name in self.values:
            self.values[value_name].init_indices(max_index)

    def parse_file(self, config_parser, max_index=None, config_directory=None):

        self.config_directory = config_directory

        if self.is_indexed and max_index is None:
            return  # if we do not know the index lets skip instead of crashing

        if not self.is_indexed:
            max_index = None
        else:
            self.max_index = max_index

        for value_name in self.values:
            self.values[value_name].parse_file(config_parser, value_name, max_index=max_index)

    def reset(self):
        for value_name in self.values:
            self.values[value_name].reset()

    def __str__(self):
        string = ''
        for value_name in self.values:
            if self.is_indexed:
                string += self.get_indexed_string(value_name)
                string += '\n'
            else:
                string += self.get_string(value_name)
        return string

    def copy(self):
        new_header = ConfigHeader()
        new_header.is_indexed = self.is_indexed
        new_header.max_index = self.max_index
        for value_name, value in self.values.items():
            new_header.values[value_name] = value.copy()
        new_header.config_directory = self.config_directory
        return new_header

    def get_indexed_string(self, value_name):
        value = self.values[value_name]
        string = value.comment_description() + '\n'
        for i in range(self.max_index):
            string += value_name + '_' + str(i) + ' = ' + str(value.get_value(index=i)) + '\n'
        return string

    def get_string(self, value_name):
        value = self.values[value_name]
        string = value.comment_description() + '\n'
        multiline_safe_value = str(value.get_value()).replace('\n', '\n\t')
        string += value_name + ' = ' + multiline_safe_value + '\n'
        return string


class ConfigValue:
    def __init__(self, value_type, default=None, description="", value=None):
        self.type = value_type
        self.value = value
        self.default = default
        self.description = description

    def get_value(self, index=None):
        """
        Returns the default if value is none.
        :param index:
        :return: A value.
        """

        if self.value is None:
            return self.default
        if index is not None:
            if self.value[index] is None:
                return self.default
            else:
                value = self.value[index]
        else:
            value = self.value

        return value

    def comment_description(self):
        return '# ' + re.sub(r'\n\s*', '\n# ', str(self.description))

    def __str__(self):
        return str(self.get_value()) + '  ' + self.comment_description()

    def copy(self):
        return ConfigValue(self.type, self.default, self.description, self.value)

    def init_indices(self, max_index):
        self.value = [None] * max_index

    def parse_file(self, config_parser, value_name, max_index=None):
        if isinstance(config_parser, ConfigHeader):
            self.value = config_parser[value_name].value
        if max_index is None:
            value = self.get_parser_value(config_parser, value_name)
            self.value = value
        else:
            self.value = []
            for i in range(max_index):
                self.value.append(self.get_parser_value(config_parser, value_name + '_' + str(i)))

    def get_parser_value(self, config_parser, value_name):
        if self.type == bool:
            return config_parser.getboolean(value_name)
        if self.type == int:
            return config_parser.getint(value_name)
        if self.type == float:
            return config_parser.getfloat(value_name)
        return config_parser.get(value_name)

    def set_value(self, value, index=None):
        if index is not None:
            self.value[index] = value
        else:
            self.value = value

    def reset(self):
        self.value = None
