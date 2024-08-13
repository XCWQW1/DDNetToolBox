import os
import sys


def get_ddnet_directory():
    system = sys.platform
    directory = None

    if system.lower().startswith('win'):
        appdata = os.getenv('APPDATA', '')
        if os.path.isdir(os.path.join(appdata, 'DDNet')):
            directory = os.path.join(appdata, "DDNet")
        else:
            directory = os.path.join(appdata, "Teeworlds")
    elif system.lower().startswith('darwin'):
        if os.path.isdir(os.path.join(os.getenv('HOME'), 'Library/Application Support/DDNet')):
            directory = os.path.join(os.getenv("HOME"), "Library/Application Support/DDNet")
        else:
            directory = os.path.join(os.getenv("HOME"), "Library/Application Support/Teeworlds")
    else:
        data_home = os.getenv('XDG_DATA_HOME', os.path.join(os.getenv('HOME'), '.local/share'))
        if os.path.isdir(os.path.join(data_home, 'ddnet')):
            directory = os.path.join(data_home, "ddnet")
        else:
            directory = os.path.join(os.getenv("HOME"), ".teeworlds")

    if directory is None:
        return "./"
    else:
        return directory
