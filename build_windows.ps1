$ErrorActionPreference='Stop'
Set-Location $PSScriptRoot
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name polarwriter --icon polarwriter.ico --add-data 'polarwriter.ico;.' app.py
