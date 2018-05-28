import json


def parse_item_lines(item_lines):
    item_dict = {}
    for _line in item_lines:
        split_line = [x.strip() for x in _line.split(':')]
        key = split_line[0]
        value = ''.join(split_line[1:])
        if not key:
            continue
        if value == 'Yes':
            value = True
        elif value == 'No':
            value = False
        item_dict[key] = value
    return item_dict


def get_items_category(items_list):
        category_words = {
            "Bodies": ['body'],
            "Decals": ['skin', 'skins'],
            "Wheels": ['wheel'],
            "Boosts": ['boost'],
            "Antennas": ['flag', 'countryflag', 'streamerflag', 'tourneyflag', 'antenna', 'pennant', 'at'],
            "Toppers": ['hat', 'crown'],
            "Trails": ['ss'],
            "GoalExplosions": ['explosion'],
            "Paints": ['paintfinish'],
            "Banners": ['playerbanner'],
            "EngineAudio": ['engineaudio'],
            # "Unwanted": ['bots', 'key', 'pack', 'itemcontainer', 'blackmarkettest', 'seasonlogos']
            "_Bots": ['bots'],
            "_Keys": ['key'],
            "_Crates": ['itemcontainer'],
            "_DLC": ['pack'],
            "_MysteryDecal": ['blackmarkettest'],
            "_SeasonLogos": ['seasonlogos']
        }

        categorised_items = {category: [] for category in category_words}
        uncategoried_items = []
        multicategorised_items = []
        for item in items_list:
            detected_item_categories = set()
            item_types = [word.lower() for word in item['AssetPackageName'].split('_')]
            for item_type in item_types:
                for category in category_words:
                    if item_type in category_words[category]:
                        detected_item_categories.add(category)
                        break
            detected_item_categories = list(detected_item_categories)

            # priority stuff
            if len(detected_item_categories) == 2 and 'Decals' in detected_item_categories and \
                    'Bodies' in detected_item_categories:
                detected_item_categories = ['Decals']
            elif '_MysteryDecal' in detected_item_categories:
                detected_item_categories = ['_MysteryDecal']

            if len(detected_item_categories) == 0:
                uncategoried_items.append(item)
                print('Detected uncategorised item: %s' % item['LongLabel'])
            elif len(detected_item_categories) == 1:
                categorised_items[detected_item_categories[0]].append(item)
                item["Category"] = detected_item_categories[0]
            else:
                print('Detected multicategorised item: %s' % item['LongLabel'])
                multicategorised_items.append((item, detected_item_categories))
                print(item['LongLabel'], detected_item_categories, item_types)

            # test for item
            # if item['Label'] == 'DC Comics':
            #     print(item['LongLabel'], detected_item_categories, item_types)
        return items_list

def get_item_id_dict(items_list):
    """
    :param items_list:
    :return items_dict: {id: {item}, id2: {item2}}
    """

    items_dict = {}

    for item in items_list:
        item_id = int(item["ID"])
        assert item_id not in items_dict, \
            "Item ID %s already in dict:\n   In dict: %s\n   To add: %s" % (item_id, items_dict[item_id], item)
        items_dict[item_id] = item

    return items_dict


if __name__ == '__main__':
    all_items = []

    with open('Rocket_League_Items.txt', 'r') as f:
        current_item_lines = []
        for line in f:
            if line.startswith('Label'):
                item = parse_item_lines(current_item_lines)
                if item:
                    all_items.append(item)
                # new item
                current_item_lines = []
            current_item_lines.append(line)
    # print(all_items)

    sorted_all_items = {}
    # sort by type
    for item in all_items:
        item_type = item['AssetPackageName'].split('_')[0].lower()
        try:
            sorted_all_items[item_type].append(item)
        except KeyError:
            sorted_all_items[item_type] = [item]
    print(sorted_all_items.keys())

    items_list = get_items_category(all_items)
    items_dict = get_item_id_dict(items_list)

    with open('rlbot/gui/categorised_items.json', 'w') as f:
        json.dump(items_dict, f)
