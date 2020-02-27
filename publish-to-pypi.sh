set -e  # exit on first failure

# Argument parsing
TEST='test'
PROD='prod'
if [ ! "$1" ] || [ "$1" != $TEST ] && [ "$1" != $PROD ]
then
    echo "Must give either '$PROD' or '$TEST' as an argument to this script."
    exit 1
fi
echo "publishing to pypi $1..."

# Check that prerequisites exist
if [ ! -f ~/.pypirc ]
then
    echo "~/.pypirc is missing. see https://github.com/RLBot/RLBot/wiki/Deploying-Changes#first-time-setup"
    exit 1
fi

# Copy things into ./build/python-dist
rm -rf ./build/python-dist
mkdir -p ./build/python-dist
./src/main/flatbuffers/flatc --python -o ./src/generated/python ./src/main/flatbuffers/rlbot.fbs
cp -r ./src/generated/python/rlbot/* ./src/main/python/rlbot/messages/
rsync -a -r \
    --exclude="*/__pycache__" \
    --exclude="rlbot.egg-info" \
    --exclude="*.iml" \
    ./src/main/python/* \
    ./build/python-dist
cp ./LICENSE.txt ./build/python-dist

# Upload to pypi.
cd build/python-dist
if [ "$1" = $PROD ]
then
    python3 setup.py sdist upload
elif [ "$1" = $TEST ]
then
    python3 setup.py sdist upload -r pypitest
else
    echo "Must give either '$PROD' or '$TEST' as an argument to this script."
    exit 1
fi
