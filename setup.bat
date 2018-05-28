@rem Change the working directory to the location of this file so that relative paths will work

@echo off

cd /D "%~dp0"

.\src\main\flatbuffers\flatc.exe --python -o .\src\generated\python .\src\main\flatbuffers\rlbot.fbs
xcopy /s /Y .\src\generated\python\rlbot .\src\main\python\rlbot\messages\

.\src\main\flatbuffers\flatc.exe --cpp -o .\src\generated\cpp\flatbuffers .\src\main\flatbuffers\rlbot.fbs

.\src\main\flatbuffers\flatc.exe --java -o .\src\generated\java\flatbuffers .\src\main\flatbuffers\rlbot.fbs

echo.
echo #######################
echo ### Setup Complete! ###
echo #######################
echo.

pause
