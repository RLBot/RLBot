@rem Change the working directory to the location of this file so that relative paths will work
@cd /D "%~dp0"


cmake --build .\src\main\cpp\RLBotInterface\build32 --config Release

copy /Y .\src\main\cpp\RLBotInterface\build32\Release\RLBotInterface.dll ^
.\src\main\python\rlbot\dll\RLBot_Core_Interface_32.dll


cmake --build .\src\main\cpp\RLBotInterface\build64 --config Release

copy /Y .\src\main\cpp\RLBotInterface\build64\Release\RLBotInterface.dll ^
 .\src\main\python\rlbot\dll\RLBot_Core_Interface.dll

copy /Y .\src\main\cpp\RLBotInterface\build64\Release\RLBot.exe ^
 .\src\main\python\rlbot\dll\RLBot.exe

pause
