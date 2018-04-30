### About

The RLBotInterface solution builds an "interface" DLL that can communicate with
a second closed-source DLL that gets injected into the game.

### Setup Instructions

1. Install Visual Studio 2015
2. Execute `./gradlew.bat assembleProtos` from the root of the repository.
This will generate a few source and header files that are needed to build successfully.
3. Open `RLBotInterface.sln` in Visual Studio

### Building the Interface DLL

1. In the Solution Platforms dropdown in the toolbar, select x64
2. Build -> Build Solution
3. Find the build output in `RLBot Core\Bin\x64\Debug` or `RLBot Core\Bin\x64\Release`

### Testing your changes

1. Build the DLL and copy it to `src\main\python\RLBotFramework\dll\RLBot_Core_Interface.dll`
2. Run RLBot as normal, e.g. `python runner.py`

Note that if you change code in the RLBotMessages project, you may break compatibility with
RLBot_Core.dll and it will need to be recompiled. The core DLL is closed source,
so you might not have access to it.