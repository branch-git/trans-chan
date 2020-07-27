@echo off
rem 文字エンコードの確認
chcp 65001

setlocal

start https://www.python.org/ftp/python/3.8.5/python-3.8.5-amd64.exe

rem 難しいコマンドたち
rem bitsadmin /transfer download https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%%2F768952%%2Fchrome-win.zip?generation=1589490546798193^&alt=media %USERPROFILE%\Desktop\chrome-win.zip
rem curl -o %USERPROFILE%\Desktop\chrome-win.zip "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%%2F768952%%2Fchrome-win.zip?generation=1589490546798193^&alt=media"

rem curl --noproxy www.googleapis.com -o %USERPROFILE%\Desktop\chrome-win.zip "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%%2F768952%%2Fchrome-win.zip?generation=1589490546798193&alt=media"
rem 素直に動いてくれるコマンドたち

start https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Win_x64%%2F768952%%2Fchrome-win.zip?generation=1589490546798193^&alt=media
echo DLが完了したら[Enter]keyを押してください && pause
Powershell -command "Expand-Archive -Path $env:USERPROFILE\Downloads\Win_x64_768952_chrome-win.zip -DestinationPath C:\Program` Files"
del %USERPROFILE%\Downloads\python-3.8.5-amd64.exe
del %USERPROFILE%\Downloads\Win_x64_768952_chrome-win.zip

py -m pip install chromedriver_binary==84.0.4147.30.0
py -m pip install wxpython
py -m pip install pyperclip
py -m pip install selenium
py -m pip install beautifulsoup4

call initialize.bat
endlocal
exit