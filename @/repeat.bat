@echo off

if "%~4"=="" (
    echo Please provide four arguments for the Python script
    exit /b 1
)

set arg1=%~1
set arg2=%~2
set arg3=%~3
set arg4=%~4

rem Loop 5 times
for /L %%i in (1,1,5) do (
    python edit.py "%arg1%" "%arg2%" "%arg3%" "%arg4%"
)

