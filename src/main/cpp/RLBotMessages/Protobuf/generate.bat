@rem Change the working directory to the location of this file so that relative paths will work
cd /D "%~dp0"

@rem Regenerate the protobuf headers and classes to ensure they are in sync with the proto file
.\protoc.exe --proto_path=. --cpp_out=. game_data.proto

pause
