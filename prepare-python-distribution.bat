rmdir /s /q .\build\python-dist\
mkdir .\build\python-dist

.\src\main\flatbuffers\flatc.exe --python -o .\src\generated\python .\src\main\flatbuffers\rlbot.fbs
xcopy /s /q /Y .\src\generated\python\rlbot .\src\main\python\rlbot\messages\

robocopy .\src\main\python .\build\python-dist /S /XD __pycache__ rlbot.egg-info /XF *.iml > nul
copy .\LICENSE.txt .\build\python-dist
