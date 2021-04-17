# RLBotDotNet

This is the .NET port of the RLBot bot manager. It was written in C#, but the DLL produced by this can be used by any .NET language.

Please run setup.bat so that the Flatbuffers generated files go in the /flat folder.

## Publishing to NuGet

RLBotDotNet is available on NuGet at https://www.nuget.org/packages/RLBot.Framework.

To publish new versions there:
1. Modify RLBotDotNet.csproj to have an incremented version number.
1. Modify RLBotDotNet.csproj to update the release notes, etc.
1. Make sure RLBotDotNet has been built with the Release configuration, on the "Any CPU" platform.
   - This should generate `.nupkg` and `.snupkg` files.
1. Go to https://www.nuget.org/packages/manage/upload and log in with our rlbotofficial account.
1. Upload the `.nupkg` file, then upload the `.snupkg` file.
