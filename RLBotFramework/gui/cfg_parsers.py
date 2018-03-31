import json
import configparser as cp

class LoadoutPreset(cp.ConfigParser):

    ITEMS_DICT_JSON = 'categorised_items.json'

    @classmethod
    def parse_items_dict_json(cls):
        with open(cls.ITEMS_DICT_JSON, 'r') as f:
            cls.ITEMS_DICT = json.load(f)

    def __init__(self):
        super().__init__()

    def read(self, file_name):
        self.file_name = file_name
        return super().read(file_name)



if __name__ == '__main__':
    LoadoutPreset.parse_items_dict_json()
    print(LoadoutPreset.ITEMS_DICT)