import os
import atexit
import configparser


TAGAME_CONFIG_LOCATION = os.path.expanduser("~/Documents/My Games/Rocket League/TAGame/Config")


def mergeTASystemSettings():
    """
    Backs up TASystemSettings.ini and creates a new merged TASystemSettings.ini based on TASystemSettings.RLBot.ini.
    Does nothing if no TASystemSettings.RLBot.ini is found.
    """
    TASystemSettings_path = os.path.join(TAGAME_CONFIG_LOCATION, "TASystemSettings.ini")
    TASystemSettings_user_path = os.path.join(TAGAME_CONFIG_LOCATION, "TASystemSettings.user.ini")
    TASystemSettings_RLBot_path = os.path.join(TAGAME_CONFIG_LOCATION, "TASystemSettings.RLBot.ini")

    # only mess with TASystemSettings if TASystemSettings.RLBot.ini exists
    if not os.path.exists(TASystemSettings_RLBot_path):
        return
    # don't mess with TASystemSettings if it has already been messed with.
    if os.path.exists(TASystemSettings_user_path):
        return

    print("Merging TASystemSettings.")

    atexit.register(cleanUpTASystemSettings)

    os.rename(TASystemSettings_path, TASystemSettings_user_path)

    config = configparser.ConfigParser()
    config.read(TASystemSettings_user_path)
    config.read(TASystemSettings_RLBot_path)
    with open(TASystemSettings_path, 'w') as configfile:
        config.write(configfile)

def cleanUpTASystemSettings():
    """
    Reverses the effects of mergeTASystemSettings.
    """
    TASystemSettings_path = os.path.join(TAGAME_CONFIG_LOCATION, "TASystemSettings.ini")
    TASystemSettings_user_path = os.path.join(TAGAME_CONFIG_LOCATION, "TASystemSettings.user.ini")

    if not os.path.exists(TASystemSettings_user_path):
        return

    print("Reverting TASystemSettings.")
    if os.path.exists(TASystemSettings_path):
        os.remove(TASystemSettings_path)

    os.rename(TASystemSettings_user_path, TASystemSettings_path)

    atexit.unregister(cleanUpTASystemSettings)