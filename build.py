import os
import subprocess
import sys
from pathlib import Path
import nicegui

cmd = [
    sys.executable,  # venv python executable
    '-m', 'PyInstaller',
    'app_main.py',  # your main file with ui.run()
    '--name', 'CicadaApp',  # name of your app
    '--onefile',
    '--windowed',  # prevent console appearing, only use with ui.run(native=True, ...)
    '--add-data', f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui'
]

if __name__ == '__main__':
    subprocess.call(cmd)
