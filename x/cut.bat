@echo off

REM Check if the required arguments are provided
if "%~4"=="" (
    echo Usage: %~nx0 input_file output_file start_time end_time
    exit /b 1
)

REM Get input arguments
set "input_file=%~1"
set "output_file=%~2"
set "start_time=%~3"
set "end_time=%~4"

REM Use ffmpeg to cut the video
ffmpeg.exe -i "%input_file%" -ss %start_time% -to %end_time% -c:v copy -c:a copy -avoid_negative_ts make_zero "%output_file%"

