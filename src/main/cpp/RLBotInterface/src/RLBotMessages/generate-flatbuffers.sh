#!/bin/bash
# change the working directory to the location of this file.
cd "$(dirname "$0")"

../../../../flatbuffers/flatc --cpp -o ../../../../../generated/cpp/flatbuffers ../../../../flatbuffers/rlbot.fbs

cd -
