import os
import subprocess
import sys

main_script = 'main.py'

files_and_folders = [
    'main.py',
    'app/',
]

# 生成Nuitka的命令
nuitka_command = [
    'python', '-m', 'nuitka',
    '--standalone',
    '--onefile',
    '--enable-plugin=pyqt5',
    '--include-qt-plugins=sensible',
    '--windows-icon-from-ico=app/resource/logo.ico',
    '--output-dir=build',
    '--remove-output',
]

if sys.platform.lower().startswith('darwin'):
    nuitka_command.append('--macos-create-app-bundle')

# 添加数据文件和文件夹
for item in files_and_folders:
    abs_path = os.path.abspath(item)
    if os.path.isdir(abs_path):
        nuitka_command.extend([
            f'--include-data-dir={abs_path}={item}'
        ])
    else:
        nuitka_command.extend([
            f'--include-data-file={abs_path}={item}'
        ])


nuitka_command.append(main_script)
subprocess.run(nuitka_command)
