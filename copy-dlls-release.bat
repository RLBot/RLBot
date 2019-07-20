@rem Change the working directory to the location of this file so that relative paths will work
@cd /D "%~dp0"


copy /Y .\src\main\cpp\RLBotInterface\RLBotInterface\Bin\x64\Release\RLBot_Core_Interface.dll ^
 .\src\main\python\rlbot\dll\RLBot_Core_Interface.dll

copy /Y .\src\main\cpp\RLBotInterface\RLBotInterface\Bin\Win32\Release\RLBot_Core_Interface.dll ^
 .\src\main\python\rlbot\dll\RLBot_Core_Interface_32.dll

copy /Y .\src\main\cpp\RLBotInterface\RLBotInterface\Bin\x64\Release\RLBot.exe ^
 .\src\main\python\rlbot\dll\RLBot.exe

pause
