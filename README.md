# Video Processing Toolkit

A comprehensive Python-based video processing toolkit that provides multiple commands for video editing, remixing, organization, and enhancement using MoviePy and FFmpeg.

## Features

- **Remix videos** from random segments with speed variations and overlap prevention
- **Generate videos** from JSON configurations with music, logos, and effects
- **Organize files** automatically by filename patterns
- **Edit videos** using XSPF playlist bookmarks
- **Add letterbox effects** and trim videos
- **Comprehensive logging** with colored output and UTF-8 support
- **Cross-platform compatibility** (Windows, Linux, macOS)

## Requirements

### Dependencies
```bash
pip install moviepy click tqdm
```

### External Tools
- **FFmpeg**: Required for video processing
  - Windows: Download from https://ffmpeg.org/download.html
  - Linux: `sudo apt install ffmpeg` or `sudo yum install ffmpeg`
  - macOS: `brew install ffmpeg`

- **ImageMagick** (optional): Required for text overlays in generate command
  - Windows: Download from https://imagemagick.org/script/download.php
  - Linux: `sudo apt install imagemagick`
  - macOS: `brew install imagemagick`

## Installation

1. Clone or download the script
2. Install Python dependencies: `pip install moviepy click tqdm`
3. Ensure FFmpeg is installed and accessible in PATH
4. Run: `python video_editor.py --help`

## Commands

### 1. Remix Command

Create videos from random segments with speed variations and overlap prevention.

```bash
python video_editor.py remix INPUT_FOLDER OUTPUT_DIRECTORY [OPTIONS]
```

**Arguments:**
- `INPUT_FOLDER`: Directory containing source videos
- `OUTPUT_DIRECTORY`: Directory where the remix video will be saved

**Options:**
- `--min-duration`: Minimum duration in seconds (default: 60)
- `--max-duration`: Maximum duration in seconds (default: 120)
- `--extensions`: Video file extensions to process (default: mp4,avi,mov,mkv)

**Example:**
```bash
python video_editor.py remix ./source_videos ./output --min-duration 90 --max-duration 180
```

**Output:** Automatically generates files with names like `remix_a1b2c3d4_.mp4`

### 2. Generate Command

Generate videos from JSON configuration files with music, logos, and effects.

```bash
python video_editor.py generate --config CONFIG_FILE
```

**Configuration File Example:**
```json
{
  "input_video": "./source.mp4",
  "music": "./audio.mp3",
  "cycle": 4,
  "speed": 1.2,
  "logo_text": "MY BRAND",
  "font": "./fonts/font.otf",
  "cut_size": 5,
  "output": "./output/generated.mp4",
  "no_rotate": false
}
```

**Multiple Videos Configuration:**
```json
{
  "videos": [
    {
      "input_video": "./video1.mp4",
      "music": "./music1.mp3",
      "repeat": 3
    },
    {
      "input_video": "./video2.mp4",
      "music": "./music2.mp3",
      "repeat": 2
    }
  ]
}
```

**Configuration Options:**
- `input_video`: Path to source video file
- `music`: Path to audio file to overlay
- `cycle`: Number of random cuts to make (default: 4)
- `speed`: Speed multiplier for video (default: 1.2)
- `logo_text`: Text to overlay on video (default: "UTOPIA")
- `font`: Path to font file for text overlay
- `cut_size`: Duration of each cut in seconds (default: 5)
- `output`: Output filename (auto-generated if not specified)
- `no_rotate`: Skip 270° rotation if true (default: false)
- `repeat`: Number of times to process this configuration

### 3. Tidy Command

Organize files in a directory by splitting filenames and using a specific part as folder name.

```bash
python video_editor.py tidy DIRECTORY INDEX [--dry-run]
```

**Arguments:**
- `DIRECTORY`: Directory containing files to organize
- `INDEX`: Which part of the filename (split by '_') to use for folder names

**Options:**
- `--dry-run`: Show what would be done without actually moving files

**Example:**
```bash
# For files like "project_alpha_001.mp4", "project_beta_002.mp4"
python video_editor.py tidy ./files 1 --dry-run
# Would create folders ALPHA, BETA and move files accordingly
```

### 4. Bookmarks Command

Edit videos using bookmark times from XSPF playlist files.

```bash
python video_editor.py bookmarks VIDEO_FILE PLAYLIST_FILE [OPTIONS]
```

**Arguments:**
- `VIDEO_FILE`: Source video file
- `PLAYLIST_FILE`: XSPF playlist file containing bookmarks

**Options:**
- `--output`: Output filename (auto-generated if not specified)
- `--codec`: Video codec (default: libx264)
- `--quality`: CRF value for quality (default: 24)
- `--preset`: Encoding preset (default: veryfast)
- `--fps`: Output FPS (default: 24)
- `--threads`: Number of encoding threads (default: 4)

**Example:**
```bash
python video_editor.py bookmarks video.mp4 bookmarks.xspf --output edited.mp4
```

### 5. Letterbox Command

Add black bars to videos and optionally trim from start/end.

```bash
python video_editor.py letterbox INPUT_FILE OUTPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE`: Source video file
- `OUTPUT_FILE`: Output video file

**Options:**
- `--top`: Height of top black bar in pixels (default: 30)
- `--bottom`: Height of bottom black bar in pixels (default: 30)
- `--cut-start`: Duration to cut from beginning in seconds (default: 0.0)
- `--cut-end`: Duration to cut from end in seconds (default: 0.0)

**Example:**
```bash
python video_editor.py letterbox input.mp4 output.mp4 --top 50 --bottom 50 --cut-start 2.5 --cut-end 1.0
```

## Directory Structure

The script creates the following directories automatically:

```
project/
├── video_editor.py          # Main script
├── logs/                    # Log files with timestamps
├── dist/                    # Generated videos (generate command)
├── src/                     # Edited videos (bookmarks command)
├── fonts/                   # Font files for text overlays
└── tracks/                  # Audio files
```

## Logging

All operations are logged with:
- **Console output**: Colored, real-time feedback
- **File logging**: Detailed logs saved in `./logs/` directory
- **UTF-8 encoding**: Supports international characters in filenames
- **Timestamps**: All log entries include precise timestamps

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Ensure FFmpeg is installed and in your system PATH
   - On Windows, the script checks for both `ffmpeg.exe` and `ffmpeg`

2. **Unicode filename errors**
   - Fixed in latest version with UTF-8 logging support
   - Supports international characters in filenames

3. **Memory issues with large videos**
   - The script includes proper resource cleanup
   - Consider processing smaller batches of videos

4. **Permission errors**
   - Ensure write permissions for output directories
   - Run with appropriate user permissions

### Performance Tips

- Use SSD storage for better I/O performance
- Increase `--threads` parameter for faster encoding
- Use `ultrafast` preset for quicker processing (lower quality)
- Close other applications to free up system resources

## Examples

### Complete Workflow Example

```bash
# 1. Organize your source videos
python video_editor.py tidy ./raw_videos 1

# 2. Create a remix from organized videos
python video_editor.py remix ./raw_videos/ACTION ./output

# 3. Generate a custom video with music and logo
python video_editor.py generate --config my_config.json

# 4. Add letterbox effect to final video
python video_editor.py letterbox ./output/final.mp4 ./final_letterbox.mp4 --top 40 --bottom 40
```

### Batch Processing with JSON

```json
{
  "videos": [
    {
      "input_video": "./clips/video1.mp4",
      "music": "./music/track1.mp3",
      "logo_text": "BRAND A",
      "repeat": 5
    },
    {
      "input_video": "./clips/video2.mp4",
      "music": "./music/track2.mp3",
      "logo_text": "BRAND B",
      "repeat": 3
    }
  ]
}
```

## License

This toolkit is provided as-is for educational and personal use. Please ensure you have appropriate rights to any media files you process.

## Contributing

Feel free to submit issues, feature requests, or improvements to enhance the toolkit's functionality.
