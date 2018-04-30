@rem Change the working directory to the location of this file so that relative paths will work
cd /D "%~dp0"

.\capnp.exe compile -oc++ -ojava game_data.capnp -I ..\cpp\RLBotInterface\lib\capnproto\include

