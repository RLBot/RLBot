from datetime import date
# data in the form of: ID,FullName,AssetPackageName,AsciiLabel,PackID,Quality,UnlockMethod

dump_file = input('Data dump (input) file name?->')
data = open(dump_file, 'r')

Bodies, Wheels, Boosts, Antennas, Decals, Toppers, Trails, Goal_Explosions, Paints, Banners, Engine_Audio = [
], [], [], [], [], [], [], [], [], [], []

car_dict = {'backfire': 'Backfire', 'force': 'Breakout', 'octane': 'Octane', 'orion': 'Paladin',
            'rhino': 'Road Hog', 'spark': 'Gizmo', 'torch': 'X-Devil', 'torment': 'Hotshot', 'vanquish': 'Merc',
            'venom': 'Venom', 'import': 'Takumi', 'musclecar': 'Dominus', 'zippy': 'Zippy', 'scarab': 'Scarab',
            'interceptor': 'Ripper', 'wastelandtruck': 'Grog', 'musclecar2': 'Dominus GT', 'torch2': 'X-Devil Mk2',
            'neocar': 'Masamune', 'rhino2': 'Road Hog XL', 'takumi': 'Takumi RX-T', 'aftershock': 'Aftershock',
            'neobike': 'Esper', 'marauder': 'Marauder', 'carcar': 'Breakout Type-S', 'number6': 'Proteus',
            'cannonboy': 'Triton', 'o2': 'Octane ZSR', 'gilliam': 'Vulcan', 'bone': 'Bone Shaker',
            'scallop': 'Twin Mill III', 'endo': 'Endo', 'charged': 'Ice Charger', 'flatbread': 'Mantis',
            'pumpernickel': 'Centio V17', 'focaccia': 'Animus GP', 'challah': "'70 Dodge Charger R/T",
            'melonpan': "'99 Nissan Skyline GT-R R34", 'levain': 'Werewolf', 'greycar': 'DeLorean Time Machine',
            'darkcar': "'16 Batmobile", 'takumi_ii': 'Takumi RX-T', 'sourdough': 'Jäger 619 RS',
            'multigrain': 'Imperator DT5', 'berry': 'The Dark Knight Rises Tumbler', 'eggplant': "'89 Batmobile",
            'Universal Decal': 'Universal Decal'}

categories = {
    "Bodies": [Bodies, ['body']],
    "Decals": [Decals, ['skin']],
    "Wheels": [Wheels, ['wheel']],
    "Boosts": [Boosts, ['boost']],
    "Antennas": [Antennas, ['flag', 'antenna', 'pennant', '.at']],
    "Toppers": [Toppers, ['hat', 'crown']],
    "Trails": [Trails, ['ss']],
    "Goal_Explosions": [Goal_Explosions, ['explosion']],
    "Paints": [Paints, ['paintfinish']],
    "Banners": [Banners, ['playerbanner']],
    "Engine_Audio": [Engine_Audio, ['engineaudio']]
}

for line in data:
    line = line.lower()
    line_parts = line.split(',')
    ID = line_parts[0]
    FullName = line_parts[1]
    AssetPackageName = line_parts[2]
    AsciiLabel = line_parts[3]
    PackID = line_parts[4]
    Quality = line_parts[5]
    UnlockMethod = line_parts[6]

    # if it is platform specific, logo for season play, crate, bots, keys, packs
    if (ID == '0' or AssetPackageName == 'seasonlogos' or AssetPackageName == 'itemcontainer' or
            AssetPackageName == 'bots' or 'key' in AssetPackageName or 'pack' in AssetPackageName):
        continue

    else:
        filtered = False
        for cat in categories:
            filters = categories[cat][1]
            for filter in filters:
                if filter in FullName and not filtered:
                    name = ('{:4} - {}'.format(ID, AsciiLabel))
                    categories[cat][0].append(name)
                    filtered = True
    if not filtered:
        print('unassigned:\n', line_parts)


def write_file(categories):
    file_name = input('Clean file (output) name(with "".txt")->')
    clean_file = open(file_name, 'w')

    day = date.today()
    today = day.strftime("%d/%m/%y")
    title = "# List of Item ID's in game as of " + today + "\n\n"
    clean_file.write(title)

    clean_file.write('### ID - AsciiLabel')
    for cat in categories:
        write = '\n\n### ' + cat + '\n'
        clean_file.write(write)
        clean_file.write('```\n')
        for item in categories[cat][0]:
            clean_file.write(item)
            clean_file.write('\n')
        clean_file.write('```')
    clean_file.close()


write_file(categories)
