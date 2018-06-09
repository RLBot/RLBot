pushd ..\..\main\python

python -c "from rlbot.utils import file_util; print(file_util.contains_locked_file(file_util.get_rlbot_directory()));" > ^
%temp%\is_locked.txt

set /p is_locked= < %temp%\is_locked.txt
del %temp%\is_locked.txt

IF "%is_locked%"=="False" (
    ECHO can update rlbot!
) ELSE (
    ECHO cannot update rlbot!
)

popd
