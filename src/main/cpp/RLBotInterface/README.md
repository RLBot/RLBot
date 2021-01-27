## About

The RLBotInterface solution builds RLBot.exe which knows how to communicate with Rocket League,
and an "interface" DLL that helps bot processes send and receive data from RLBot.exe.

## Setup Instructions

### Windows

#### First time setup
1. Download cmake from https://cmake.org/download/ and install.
1. Download and install 64 bit [boost binaries](https://sourceforge.net/projects/boost/files/boost-binaries/1.67.0/boost_1_67_0-msvc-14.1-64.exe/download)
1. Download and install 32 bit [boost binaries](https://sourceforge.net/projects/boost/files/boost-binaries/1.67.0/boost_1_67_0-msvc-14.1-32.exe/download)
1. Install an IDE, e.g. CLion or Visual Studio

##### CLion
1. Open this folder in CLion as a project with existing sources.
1. Go to Settings -> Build, Execution, Deployment -> CMake
1. Set CMake options: `-DBOOST_ROOT=C:\Users\wherever\boost_1_67_0` (modify to match your location)

##### Visual Studio
1. Generate the 64 bit project files by running the following command inside the src/main/cpp/RLBotInterface folder:
`cmake -DBOOST_ROOT=<path to your boost directory> -B build64 -A x64`
1. Generate the 32 bit project files by running the following command inside the src/main/cpp/RLBotInterface folder:
`cmake -DBOOST_ROOT=<path to your boost directory> -B build32 -A Win32`
1. In Visual Studio, open src\main\cpp\RLBotInterface\build64\RLBot.sln.

The IDE should be capable of building everything successfully at this point. However,
you do NOT need to use the IDE for the final build because we have batch files for that. Read below.

#### Windows binaries

We like to build two different versions of the interface dll: x64 and x86. We ship both of them with rlbot so that
bot makers can use 32 bit or 64 bit python.

We only ship a 64 bit version of RLBot.exe.

There are batch files in the root directory of RLBot (above this directory) which can build the binaries for you.
- `copy-dlls.bat`: builds and copies the binaries in debug mode. **Please do NOT commit debug binaries or push them to pypi!**
- `copy-dlls-release.bat` :builds and copies the binaries in release mode.

### Linux
#### First time setup
1. Make sure you've run setup.sh in the root of the RLBot repo (several folders above this).
1. Download cmake, many distros have a package manager that will do that for you. 
On Ubuntu or other Debian systems you can do this with `sudo apt-get install cmake` 
Alternatively you can find the binaries on https://cmake.org/download/. 
1. Get gcc-9 according to these instructions: https://askubuntu.com/questions/1140183/install-gcc-9-on-ubuntu-18-04 (also follow the comment about update-alternatives)
1. Download and build the boost, you can find boost on https://sourceforge.net/projects/boost/files/boost/1.67.0/. Many distros have boost availabe from the package manager but they might be using an old version incompatible with rlbot.
On Ubuntu I followed these instructions: https://stackoverflow.com/a/24086375
1. Generate the 64 bit project files by running the following command inside the src/main/cpp/RLBotInterface folder:
`cmake -DBOOST_ROOT=<path to your boost directory> .`It may also be sufficient to just run `cmake .`

#### Linux binaries
1. Build the binaries by running `make` inside the src/main/cpp/RLBotInterface folder.
2. Copy the binaries to src/main/python/rlbot/dll. You should have:
  - `RLBot`
  - `libRLBotInterface.so`

### Mac

#### First time setup

1. brew install cmake
1. brew install python
1. ./setup_mac
1. Download and build boost, you can find boost on https://sourceforge.net/projects/boost/files/boost/1.67.0/.
  - Try compiling in this manner: (modified from https://stackoverflow.com/a/8497667)
  - `./bootstrap.sh --with-toolset=clang`
  - `./b2 toolset=clang cxxflags="-std=c++1z" linkflags="-std=c++1z"`
1. Generate the 64 bit project files by running the following command inside the src/main/cpp/RLBotInterface folder:
`cmake -DBOOST_ROOT=<path to your boost directory> .`

#### Mac binaries
1. Build the binaries by running `make` inside the src/main/cpp/RLBotInterface folder.
2. Run `copy-dlls-mac.sh` which is located at the root of the repository.

## Testing your changes

1. Stop any processes that may be using the dlls, e.g. rlbot, or Rocket League, which could prevent a successful file copy.
1. Build and copy the binaries (see above).
1. Run RLBot as normal, e.g. `python runner.py` or `python runner_gui.py`
  - On Mac or Linux you may need to run `python3` instead.
  - At time of writing, we are unable to launch Rocket League in -rlbot mode on Mac, so RLBot can only be used
    in remote_rlbot_client mode for now.

This should cause Rocket League to open with the -rlbot flag, and you should expect custom bots to
spawn and run successfully.
