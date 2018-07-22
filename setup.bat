@rem Change the working directory to the location of this file so that relative paths will work

@echo off

cd /D "%~dp0"

python -m pip install -r requirements.txt

.\src\main\flatbuffers\flatc.exe --python -o .\src\generated\python .\src\main\flatbuffers\rlbot.fbs
xcopy /s /Y .\src\generated\python\rlbot .\src\main\python\rlbot\messages\

.\src\main\flatbuffers\flatc.exe --cpp -o .\src\generated\cpp\flatbuffers .\src\main\flatbuffers\rlbot.fbs

.\src\main\flatbuffers\flatc.exe --java -o .\src\generated\java\flatbuffers .\src\main\flatbuffers\rlbot.fbs

.\src\main\flatbuffers\flatc.exe --csharp -o .\src\generated\cs\flatbuffers .\src\main\flatbuffers\rlbot.fbs
xcopy /s /Y .\src\generated\cs\flatbuffers\rlbot .\src\main\cs\RLBotDotNet\RLBotDotNet

.\src\main\flatbuffers\flatc.exe --js -o .\src\generated\js\flatbuffers .\src\main\flatbuffers\rlbot.fbs

echo.
echo #######################
echo ### Setup Complete! ###
echo #######################
echo.

pause
