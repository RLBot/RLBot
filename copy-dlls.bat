@rem Change the working directory to the location of this file so that relative paths will work
@cd /D "%~dp0"


cmake --build .\src\main\cpp\RLBotInterface\build32 --config Debug

copy /Y .\src\main\cpp\RLBotInterface\build32\Debug\RLBotInterface.dll ^
.\src\main\python\rlbot\dll\RLBot_Core_Interface_32.dll


cmake --build .\src\main\cpp\RLBotInterface\build64 --config Debug

copy /Y .\src\main\cpp\RLBotInterface\build64\Debug\RLBotInterface.dll ^
 .\src\main\python\rlbot\dll\RLBot_Core_Interface.dll

copy /Y .\src\main\cpp\RLBotInterface\build64\Debug\RLBot.exe ^
 .\src\main\python\rlbot\dll\RLBot.exe

pause
