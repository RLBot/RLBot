@rem Change the working directory to the location of this file so that relative paths will work

pushd "%~dp0"

echo Generating flatbuffers header file...

..\..\..\flatbuffers\flatc.exe --cpp -o ..\..\..\..\generated\cpp\flatbuffers ..\..\..\flatbuffers\rlbot.fbs

echo Done.

popd
