@rem Change the working directory to the location of this file so that relative paths will work
@cd /D "%~dp0"

cmake --build .\src\main\cpp\RLBotInterface\build64 --config Release

copy /Y .\src\main\cpp\RLBotInterface\build64\Release\RLBot.exe ^
 .\src\main\python\rlbot\dll\RLBot.exe

pause
