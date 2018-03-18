@rem Change the working directory to the location of this file so that relative paths will work
cd /D "%~dp0"

@rem Regenerate the protobuf headers and classes to ensure they are in sync with the proto file
..\packages\protobuf.cpp.redist.3.1.0\build\native\bin\x64\v140\Release\protoc.exe --proto_path=. --cpp_out=. game_data.proto
