@echo off

cd /D "%~dp0"
pushd ..\..\main\python

setlocal EnableDelayedExpansion

@rem Run the is_safe_to_upgrade function and save the output to a temp file.
python -c "from rlbot.utils import public_utils; print(public_utils.is_safe_to_upgrade());" > %temp%\is_safe_to_upgrade.txt

IF %ERRORLEVEL% NEQ 0 (
    @rem The python command failed, so rlbot is probably not installed at all. Safe to 'upgrade'.
    set is_safe_to_upgrade=True
) ELSE (
    @rem read the file containing the python output.
    set /p is_safe_to_upgrade= < %temp%\is_safe_to_upgrade.txt
)
del %temp%\is_safe_to_upgrade.txt

IF "!is_safe_to_upgrade!"=="True" (
    echo can update rlbot!
) ELSE (
    echo !is_safe_to_upgrade!
)

endlocal

popd
