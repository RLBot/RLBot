import os
import subprocess
import tempfile
from shutil import copyfile

from rlbot.utils.structures.game_interface import get_dll_directory


def copy_pitch_data_to_temp():
    pitch_data = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pitch.dat')
    destination = os.path.join(tempfile.gettempdir(), 'rlbot-pitch.dat')
    copyfile(pitch_data, destination)


def launch():
    return subprocess.Popen(os.path.join(get_dll_directory(), "BallPrediction.exe"),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
