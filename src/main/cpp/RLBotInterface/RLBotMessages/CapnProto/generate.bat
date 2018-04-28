.\capnp.exe compile -oc++ game_data.capnp -I ..\..\lib\capnproto\include
@echo off
echo.
echo ##############################
echo This should have generated game_data.capnp.h and game_data.capnp.c++
echo NOTE: Visual Studio wants .cpp, not .c++, so make sure you rename the file, replacing the existing one if necessary.
echo ##############################
echo.
pause
