python3 -m pip install -r requirements.txt --user

./src/main/flatbuffers/flatc_mac --cpp -o ./src/generated/cpp/flatbuffers ./src/main/flatbuffers/rlbot.fbs
./src/main/flatbuffers/flatc_mac --python -o ./src/generated/python ./src/main/flatbuffers/rlbot.fbs

cp -r ./src/generated/python/rlbot/ ./src/main/python/rlbot/messages/
