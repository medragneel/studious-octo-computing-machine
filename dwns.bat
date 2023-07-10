@echo off

REM Check if yt-dlp is installed
where yt-dlp >nul 2>&1
if %errorlevel% neq 0 (
    echo yt-dlp is not installed. Please install yt-dlp before running this script.
    exit /b 1
)

REM Prompt user for YouTube URL
set /p youtube_url="Enter YouTube URL: "

REM Prompt user for output directory
set /p output_dir="Enter output directory (default: music directory): "
if "%output_dir%"=="" set output_dir=.\music\new\

REM Prompt user for file format
set /p file_format="Enter file format (default: mp3): "
if "%file_format%"=="" set file_format=mp3

REM Prompt user for additional options
set /p additional_options="Enter additional options (default: none): "

REM Construct yt-dlp command with user inputs
set command=yt-dlp -f "ba" -x --audio-format %file_format% -o "%output_dir%\%%(title)s.%%(ext)s" %additional_options% %youtube_url%

REM Print the command for user confirmation
echo The following command will be executed:
echo %command%

REM Prompt user for confirmation to proceed
set /p confirm="Do you want to proceed? (y/n): "
if /i "%confirm%"=="y" (
    REM Execute the yt-dlp command
    %command%
    echo Download completed!
) else (
    echo Aborted by user.
)

