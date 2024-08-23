import subprocess

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
    '--assume-yes-for-downloads',
    '--windows-disable-console',
    '--onefile',
    '--include-data-dir=app=app'
]

print(nuitka_command)
nuitka_command.append('main.py')
subprocess.run(nuitka_command)
