import os
import platform


def get_ddnet_directory():
    system = platform.system()
    directory = None

    if system.startswith('CYGWIN') or system.startswith('MINGW') or system.startswith('MSYS'):
        appdata = os.getenv('APPDATA', '')
        if os.path.isdir(os.path.join(appdata, 'DDNet')):
            directory = os.path.join(appdata, "DDNet")
        else:
            directory = os.path.join(appdata, "Teeworlds")
    elif system == 'Darwin':
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
