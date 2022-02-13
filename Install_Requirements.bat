@echo off
echo Activating virtual environment...
echo Installing program requirements..
start env\scripts\activate.bat
pip install -r req.txt
pause
