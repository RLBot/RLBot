cd src/main/cpp/RLBotInterface
make
cd -
cp src/main/cpp/RLBotInterface/RLBot src/main/python/rlbot/dll/RLBot_mac
cp src/main/cpp/RLBotInterface/libRLBotInterface.dylib src/main/python/rlbot/dll/libRLBotInterface.dylib
