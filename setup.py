from PyInstaller.__main__ import run
import shutil
import os

main_script = 'main.py'

files_and_folders = [
    'main.py',
    'app/',
]

datas = []
for item in files_and_folders:
    abs_path = os.path.abspath(item)
    if os.path.isdir(abs_path):
        datas.append((abs_path + os.path.sep, item))
    else:
        datas.append((abs_path, '.'))

pyinstaller_command = [
    '--onefile',
    '--windowed',
    '--name=DDNetToolBox',
    '--clean',
    '--runtime-tmpdir=app/temp'
    '--icon=logo.ico',
]

for data in datas:
    pyinstaller_command.extend(['--add-data', f'{data[0]}{os.pathsep}{data[1]}'])

pyinstaller_command.append(main_script)

run(pyinstaller_command)

# shutil.copytree("build/app/resource", "dist")
