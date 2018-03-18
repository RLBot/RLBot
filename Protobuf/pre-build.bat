@rem Change the working directory to the location of this file so that relative paths will work
cd /D "%~dp0"

@rem Create a 'generated' directory to hold protobuf stuff. Clean it first if it exists.
rmdir /s /q .\generated
mkdir .\generated

@rem Copy the protobuf headers into a viable directory structure. They must be nested inside google\protobuf\.
xcopy /i /e /s /y /f ..\packages\protobuf.cpp.3.1.0\build\native\include\* .\generated\google\protobuf\
