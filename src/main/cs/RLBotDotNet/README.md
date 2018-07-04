# RLBotDotNet

This is the .NET port of the RLBot bot manager. It was written in C#, but the DLL produced by this can be used by any .NET language.

Please run setup.bat so that the Flatbuffers generated files go in the /flat folder.

## Publishing to NuGet

RLBotDotNet is available on NuGet at https://www.nuget.org/packages/RLBot.Framework.

To publish new versions there:
1. Install the NuGet CLI: https://docs.microsoft.com/en-us/nuget/install-nuget-client-tools#nugetexe-cli.
   - Put the exe on your PATH.
2. Modify AssemblyInfo.cs to have an incremented version number.
3. Make sure RLBotDotNet has been built with the Release configuration, on the "Any CPU" platform.
4. Open a terminal and go to the RLBotDotNet folder (the one that contains RLBotDotNet.csproj).
5. Run `nuget pack .\RLBotDotNet.csproj -Prop Configuration=Release`
   - This should create a file like RLBot.Framework.0.0.1.nupkg.
6. Go to https://www.nuget.org/packages/manage/upload and log in with our rlbotofficial account.
7. Upload the nupkg file.
