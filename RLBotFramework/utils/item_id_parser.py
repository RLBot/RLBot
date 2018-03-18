from datetime import date
# data in the form of: ID,FullName,AssetPackageName,AsciiLabel,PackID,Quality,UnlockMethod

dump_file = input('Data dump (input) file name?->')
data = open(dump_file, 'r')

Bodies,Wheels,Boosts,Antennas,Decals,Toppers,Trails,Goal_Explosions,Paints,Banners,Engine_Audio=[],[],[],[],[],[],[],[],[],[],[]

types={"Bodies":Bodies,"Wheels":Wheels,"Boosts":Boosts,"Antennas":Antennas,"Decals":Decals,"Toppers":Toppers,
"Trails":Trails,"Goal_Explosions":Goal_Explosions,"Paints":Paints,"Banners":Banners,"Engine_Audio":Engine_Audio}

car_dict = {'backfire': 'Backfire', 'force': 'Breakout', 'octane': 'Octane', 'orion': 'Paladin',
'rhino': 'Road Hog','spark': 'Gizmo', 'torch': 'X-Devil', 'torment': 'Hotshot', 'vanquish': 'Merc',
'venom':'Venom','import': 'Takumi', 'musclecar': 'Dominus', 'zippy': 'Zippy', 'scarab': 'Scarab',
'interceptor': 'Ripper','wastelandtruck': 'Grog', 'musclecar2': 'Dominus GT', 'torch2': 'X-Devil Mk2',
'neocar': 'Masamune','rhino2': 'Road Hog XL', 'takumi': 'Takumi RX-T', 'aftershock': 'Aftershock',
'neobike': 'Esper','marauder': 'Marauder', 'carcar': 'Breakout Type-S', 'number6': 'Proteus',
'cannonboy': 'Triton','o2': 'Octane ZSR', 'gilliam': 'Vulcan', 'bone': 'Bone Shaker',
'scallop': 'Twin Mill III', 'endo': 'Endo','charged': 'Ice Charger', 'flatbread': 'Mantis',
'pumpernickel': 'Centio V17', 'focaccia': 'Animus GP','challah': "'70 Dodge Charger R/T",
'melonpan': "'99 Nissan Skyline GT-R R34", 'levain': 'Werewolf','greycar': 'DeLorean Time Machine',
'darkcar': "'16 Batmobile",'takumi_ii': 'Takumi RX-T','sourdough': 'Jäger 619 RS',
'multigrain': 'Imperator DT5','berry': 'The Dark Knight Rises Tumbler','eggplant': "'89 Batmobile",
'Universal Decal': 'Universal Decal'}

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
    #if it is platform specific, logo for season play, crate, bots, keys, packs
    if (ID=='0' or AssetPackageName == 'seasonlogos' or AssetPackageName == 'itemcontainer' or
    AssetPackageName == 'bots' or 'key' in AssetPackageName or 'pack' in AssetPackageName):
        continue

    elif 'body' in FullName:
        body = ('{:4} - {}'.format(ID,AsciiLabel))
        Bodies.append(body)

    elif 'skin' in FullName:
        car=AssetPackageName.split('_')
        if len(car) <= 2:
            car = 'Universal Decal'
        else:
            car = car[1]
        skin = ('{:4} - {} - {}'.format(ID,AsciiLabel,car_dict[car]))
        Decals.append(skin)

    elif 'engineaudio' in FullName:
        engineaudio = ('{:4} - {}'.format(ID,AsciiLabel))
        Engine_Audio.append(engineaudio)

    elif 'flag' in FullName or 'antenna' in FullName or 'pennant' in FullName or '.at' in FullName:
        antenna = ('{:4} - {}'.format(ID,AsciiLabel))
        Antennas.append(antenna)

    elif 'playerbanner' in FullName:
        playerbanner = ('{:4} - {}'.format(ID,AsciiLabel))
        Banners.append(playerbanner)

    elif 'wheel' in FullName:
        wheel = ('{:4} - {}'.format(ID,AsciiLabel))
        Wheels.append(wheel)

    elif 'boost' in FullName:
        boost = ('{:4} - {}'.format(ID,AsciiLabel))
        Boosts.append(boost)

    elif 'explosion' in FullName:
        explosion = ('{:4} - {}'.format(ID,AsciiLabel))
        Goal_Explosions.append(explosion)

    elif 'hat' in FullName or 'crown' in FullName:
        hat = ('{:4} - {}'.format(ID,AsciiLabel))
        Toppers.append(hat)

    elif 'paintfinish' in FullName:
        paintfinish = ('{:4} - {}'.format(ID,AsciiLabel))
        Paints.append(paintfinish)

    elif 'ss' in FullName: #trails
        trail = ('{:4} - {}'.format(ID,AsciiLabel))
        Trails.append(trail)

    else:
        print('unassigned:\n',line_parts)

def write_file(types):
    file_name = input('Clean file (output) name(with "".txt")->')
    clean_file = open(file_name, 'w')

    day = date.today()
    today=day.strftime("%d/%m/%y")
    title="# List of Item ID's in game as of "+today+"\n\n"
    clean_file.write(title)

    clean_file.write('### ID - AsciiLabel')
    for type in types:
        write='\n\n### '+type+'\n'
        clean_file.write(write)
        clean_file.write('```\n')
        for item in types[type]:
            clean_file.write(item)
            clean_file.write('\n')
        clean_file.write('```')
    clean_file.close()

write_file(types)
