### About

The RLBotInterface solution builds an "interface" DLL that can communicate with
a second closed-source DLL that gets injected into the game.

### Setup Instructions

1. Install Visual Studio 2015
2. Open `RLBotInterface.sln` in Visual Studio

### Building the Interface DLLs

We like to build two different versions of the interface dll: x64 and x86. We ship both of them with rlbot so that
bot makers can use 32 bit or 64 bit python.

1. In the Solution Configurations dropdown in the toolbar, choose Debug or Release.
   - Debug is useful during development for setting breakpoints, etc, and we use Release when we're finished and
   ready to send the dll out to bot makers.
2. In the Solution Platforms dropdown in the toolbar, select x64
3. Build -> Build Solution
4. Find the build output in `RLBotInterface\Bin\x64\Debug` or `RLBotInterface\Bin\x64\Release`
5. In the Solution Platforms dropdown in the toolbar, select x86, then build again.

### Testing your changes

1. Build the DLL 
2. Stop any processes that may be using the dlls, e.g. rlbot, or Rocket League, which could prevent a successful file copy.
3. Copy the dll to `src\main\python\rlbot\dll\RLBot_Core_Interface.dll`. There are scripts that can do the copy for you:
   - `copy-dlls.bat` copies over dlls from the Debug output directories.
   - `copy-dlls-release.bat` copies over dlls from the Release output directories.
   - They both overwrite the same files in the same location, so choose and run only one.
   The scripts also copy in RLBot_Core.dll if you happen to have the core repository set up.
4. Run RLBot as normal, e.g. `python runner.py`

Note that if you change code in the RLBotMessages project, you may break compatibility with
RLBot_Core.dll and it will need to be recompiled. The core DLL is closed source,
so you might not have access to it.