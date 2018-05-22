@rem Change the working directory to the location of this file so that relative paths will work
@cd /D "%~dp0"


copy /Y .\src\main\cpp\RLBotInterface\RLBotInterface\Bin\x64\Debug\RLBotInterface.dll ^
 .\src\main\python\RLBotFramework\dll\RLBot_Core_Interface.dll

@echo off
echo.

setlocal enabledelayedexpansion

set /A count=0
FOR /d %%a in (..\*rlbot?core) DO (
    echo Found core folder %%a
    set core_folder=%%a
    set /A count=count+1
)

IF %count% GEQ 2 (
    echo Cannot copy core dll because more than one core directory was found. Please move one of them.
    EXIT
)

@echo on

copy /Y "%core_folder%\RLBot Core\Bin\Win32\Debug-SDK\RLBot Core.dll" ^
 .\src\main\python\RLBotFramework\dll\RLBot_Core.dll
