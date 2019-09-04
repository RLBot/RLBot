python3 -m pip install -r requirements.txt

./src/main/flatbuffers/flatc --cpp -o ./src/generated/cpp/flatbuffers ./src/main/flatbuffers/rlbot.fbs
./src/main/flatbuffers/flatc --python -o ./src/generated/python ./src/main/flatbuffers/rlbot.fbs

cp -r ./src/generated/python/rlbot/flat ./src/main/python/rlbot/messages/