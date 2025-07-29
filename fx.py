#!/usr/bin/env python3
import click
import json
import logging
import os
import sys
import shutil
import re
import random
import subprocess
import uuid
from datetime import datetime
from itertools import batched
from pathlib import Path
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

import moviepy.editor as mpy
from moviepy.video.fx.all import rotate, speedx
from moviepy.audio.fx.all import audio_fadeout, audio_fadein
from moviepy.config import change_settings
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip, concatenate_videoclips
from tqdm import tqdm

# Utility functions
def getrandomDuration(video_duration, cut_length):
    """Generate a random start time and return (start, start+cut_length) tuple."""
    max_start = max(0, video_duration - cut_length)
    start = random.uniform(0, max_start)
    end = min(start + cut_length, video_duration)
    return (start, end)

def detect_overlapping_tuples(cuts):
    """Check if any time ranges overlap."""
    sorted_cuts = sorted(cuts, key=lambda x: x[0])
    for i in range(len(sorted_cuts) - 1):
        if sorted_cuts[i][1] > sorted_cuts[i + 1][0]:
            return True
    return False

# Classes for the remix command
@dataclass
class TimeRange:
    start: float
    end: float

    def overlaps(self, other: 'TimeRange') -> bool:
        """Check if this time range overlaps with another."""
        return (self.start <= other.end and self.end >= other.start)

class UsedSegments:
    def __init__(self):
        self.segments: Dict[str, List[TimeRange]] = defaultdict(list)

    def add_segment(self, video_path: str, start: float, end: float):
        """Add a used time range for a video."""
        self.segments[video_path].append(TimeRange(start, end))

    def is_available(self, video_path: str, start: float, end: float, min_gap: float = 0.5) -> bool:
        """
        Check if a time range is available for use.
        min_gap: minimum gap required between segments (in seconds)
        """
        new_range = TimeRange(start - min_gap, end + min_gap)
        return not any(
            existing.overlaps(new_range)
            for existing in self.segments[video_path]
        )

    def get_available_duration(self, video_path: str, clip_duration: float) -> float:
        """Calculate total available duration excluding used segments."""
        used_ranges = sorted(self.segments[video_path], key=lambda x: x.start)
        total_used = sum(r.end - r.start for r in used_ranges)
        return clip_duration - total_used

class VideoProcessor:
    def __init__(self, target_duration: Tuple[int, int] = (60, 120)):
        self.min_duration = target_duration[0]
        self.max_duration = target_duration[1]
        self.loaded_clips = {}
        self.used_segments = UsedSegments()
        self.ffmpeg_path = self._check_ffmpeg()
        change_settings({"FFMPEG_BINARY": self.ffmpeg_path})

    def _check_ffmpeg(self):
        """Verify FFmpeg is accessible on Windows."""
        try:
            subprocess.run(['ffmpeg.exe', '-version'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         check=True)
            return 'ffmpeg.exe'
        except Exception:
            try:
                subprocess.run(['ffmpeg', '-version'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             check=True)
                return 'ffmpeg'
            except Exception as e:
                logging.error(f"FFmpeg check failed: {str(e)}")
                raise RuntimeError("FFmpeg not found or not working properly")

    def load_video(self, video_path: str) -> VideoFileClip:
        video_path = str(Path(video_path).resolve())
        if video_path not in self.loaded_clips:
            try:
                logging.info(f"Loading video: {video_path}")
                clip = VideoFileClip(video_path, verbose=True)
                if not clip.reader:
                    raise ValueError("Video reader not initialized")
                self.loaded_clips[video_path] = clip
                logging.info(f"Successfully loaded video: {video_path} (duration: {clip.duration:.2f}s)")
            except Exception as e:
                logging.error(f"Failed to load video {video_path}: {str(e)}")
                raise
        return self.loaded_clips[video_path]

    def find_available_segment(self, video_path: str, desired_duration: float) -> Tuple[float, float]:
        """Find an available time segment in the video that hasn't been used."""
        clip = self.load_video(video_path)
        max_attempts = 50  # Prevent infinite loops
        attempts = 0

        while attempts < max_attempts:
            start_time = random.uniform(0, max(0, clip.duration - desired_duration))
            end_time = start_time + desired_duration

            if self.used_segments.is_available(video_path, start_time, end_time):
                return start_time, end_time

            attempts += 1

        raise ValueError("Could not find an available segment after maximum attempts")

    def get_random_segment(self, video_path: str) -> VideoFileClip:
        """Extract a random segment with repetition prevention."""
        logging.info(f"Creating random segment from: {video_path}")
        clip = self.load_video(video_path)

        # Calculate available duration
        available_duration = self.used_segments.get_available_duration(video_path, clip.duration)
        if available_duration < 1:  # Minimum segment length
            raise ValueError("Not enough unused duration remaining")

        # Determine segment duration
        max_segment_duration = min(5, available_duration)
        min_segment_duration = min(1, max_segment_duration)
        segment_duration = random.uniform(min_segment_duration, max_segment_duration)

        try:
            # Find an unused time range
            start_time, end_time = self.find_available_segment(video_path, segment_duration)
            logging.info(f"Found unused segment: {start_time:.2f}s to {end_time:.2f}s")

            # Extract the segment
            segment = clip.subclip(start_time, end_time)

            # Apply speed variation
            speed_factor = random.uniform(1, 2.5)
            logging.info(f"Applying speed factor: {speed_factor:.2f}x")
            segment = segment.speedx(speed_factor)

            # Record the used segment
            self.used_segments.add_segment(video_path, start_time, end_time)

            return segment

        except Exception as e:
            logging.error(f"Failed to create segment: {str(e)}")
            raise

    def create_video(self, input_paths: List[str], output_dir: str) -> str:
        if not input_paths:
            raise ValueError("No input videos provided")

        # Generate automatic filename with UUID
        unique_id = str(uuid.uuid4())[:8]  # Use first 8 characters of UUID
        output_filename = f"remix_{unique_id}_.mp4"

        # Ensure output directory exists
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Full output path
        output_path = output_dir_path / output_filename

        logging.info(f"Starting video creation with {len(input_paths)} input files")
        logging.info(f"Generated output filename: {output_filename}")
        segments = []
        current_duration = 0
        target_duration = random.uniform(self.min_duration, self.max_duration)

        try:
            available_videos = input_paths.copy()
            max_attempts = 100  # Prevent infinite loops
            attempts = 0

            while current_duration < target_duration and attempts < max_attempts:
                if not available_videos:
                    logging.warning("No more available videos with unused segments")
                    break

                video_path = random.choice(available_videos)

                try:
                    segment = self.get_random_segment(video_path)
                    segments.append(segment)
                    current_duration += segment.duration
                    logging.info(f"Added segment (duration: {segment.duration:.2f}s, total: {current_duration:.2f}s)")

                except ValueError as e:
                    logging.warning(f"No more unused segments in {video_path}: {str(e)}")
                    available_videos.remove(video_path)
                except Exception as e:
                    logging.warning(f"Error processing {video_path}: {str(e)}")
                    available_videos.remove(video_path)

                attempts += 1

            if not segments:
                raise Exception("Failed to create any valid segments")

            logging.info("Concatenating segments...")
            final_video = concatenate_videoclips(segments, method="compose")

            output_path_str = str(output_path.resolve())
            logging.info(f"Writing final video to: {output_path_str}")

            final_video.write_videofile(
                output_path_str,
                fps=24,
                codec='libx264',
                audio=False,
                preset='ultrafast',
                threads=4,
                verbose=False,
                ffmpeg_params=['-hide_banner', '-loglevel', 'error']
            )

            return output_path_str

        except Exception as e:
            logging.error(f"Error in video creation: {str(e)}")
            raise
        finally:
            logging.info("Cleaning up resources...")
            for clip in segments:
                try:
                    clip.close()
                except Exception as e:
                    logging.warning(f"Error closing segment: {str(e)}")

            for clip in self.loaded_clips.values():
                try:
                    clip.close()
                except Exception as e:
                    logging.warning(f"Error closing clip: {str(e)}")

def setup_logging():
    """Set up logging configuration with colored output and detailed formatting."""
    os.makedirs('./logs', exist_ok=True)
    log_filename = f"./logs/video_editor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[94m',    # Blue
            'INFO': '\033[92m',     # Green
            'WARNING': '\033[93m',  # Yellow
            'ERROR': '\033[91m',    # Red
            'CRITICAL': '\033[1;31m'  # Bold Red
        }
        RESET = '\033[0m'

        def format(self, record):
            log_message = super().format(record)
            color = self.COLORS.get(record.levelname, '')
            return f"{color}{log_message}{self.RESET}"

    # Configure console handler with UTF-8 encoding
    console_handler = logging.StreamHandler()
    console_handler.stream = sys.stdout

    # Configure file handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')

    console_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[console_handler, file_handler],
        force=True
    )

    return logging.getLogger(__name__)

def set_imagemagick_path():
    """Set the ImageMagick path based on the operating system."""
    if os.name == 'nt':
        imagemagick_path = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
    else:
        imagemagick_path = "/usr/local/bin/convert"

    if os.path.exists(imagemagick_path):
        change_settings({"IMAGEMAGICK_BINARY": imagemagick_path})
        logging.info(f"ImageMagick path set to: {imagemagick_path}")
    else:
        logging.warning(f"ImageMagick not found at {imagemagick_path}. Please install it or update the path.")

# Helper functions for the generate command
def generate_cuts(video, cycle, length):
    """Generate non-overlapping random cuts for the video."""
    while True:
        cuts = [getrandomDuration(video.duration, length) for _ in range(cycle)]
        cts = list({tuple(cut): None for cut in cuts}.keys())
        if not detect_overlapping_tuples(cts):
            break
    return cts

def process_clip(video, cut):
    """Process a single video clip with a crossfade effect."""
    return video.subclip(cut[0], cut[1]).crossfadein(1)

def edit_video(config, logger, iteration=1):
    """Edit video based on configuration."""
    # Extract configuration
    input_video = config.get("input_video")
    music = config.get("music")
    cycle = config.get("cycle", 4)
    no_rotate = config.get("no_rotate", False)
    speed = config.get("speed", 1.2)
    output = config.get("output", "")
    logo_text = config.get("logo_text", "UTOPIA")
    font = config.get("font", "./fonts/Anurati-Regular.otf")
    cut_size = config.get("cut_size", 5)

    # Input validation
    if not os.path.exists(input_video):
        logger.error(f"Input video file '{input_video}' not found.")
        return
    if not os.path.exists(music):
        logger.error(f"Music file '{music}' not found.")
        return

    logger.info(f"Processing video: {input_video}")
    logger.info(f"Using music: {music}")

    try:
        video = mpy.VideoFileClip(input_video, audio=False)
        cts = generate_cuts(video, cycle, cut_size)

        # Process clips sequentially
        clips = [process_clip(video, cut) for cut in cts]

        final_clip = mpy.concatenate_videoclips(clips, method="compose").fx(speedx, speed)

        if not no_rotate:
            final_clip = final_clip.fx(rotate, 270)

        audio = mpy.AudioFileClip(music)
        new_audioclip = mpy.CompositeAudioClip([audio])
        new_audioclip = new_audioclip.set_duration(final_clip.duration)
        new_audioclip = new_audioclip.fx(audio_fadein, duration=2.0)
        new_audioclip = new_audioclip.fx(audio_fadeout, duration=1.0)
        final_clip = final_clip.set_audio(new_audioclip)

        logo = (
            mpy.TextClip(logo_text, fontsize=30, color="white", font=font)
            .set_position((60, 60))
            .set_opacity(0.7)
            .set_duration(final_clip.duration)
        )

        final = mpy.CompositeVideoClip([final_clip, logo])
        final = final.set_fps(30)

        # Determine output filename
        if not output:
            dt = datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"./dist/final_{dt}_{iteration}.mp4"
        else:
            name, ext = os.path.splitext(output)
            output_filename = f"{name}_{iteration}{ext}"

        # Ensure dist directory exists
        os.makedirs('./dist', exist_ok=True)

        logger.info(f"Writing video to: {output_filename}")
        final.write_videofile(
            output_filename,
            threads=6,
            fps=30,
            codec="libx264",
            preset="ultrafast",
            ffmpeg_params=["-crf", "30"],
            audio_codec="aac",
        )

        logger.info(f"Successfully processed video: {output_filename}")
        video.close()

    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")

# CLI Commands
@click.group()
def cli():
    """Video processing toolkit with multiple commands."""
    pass

@cli.command()
@click.argument('input_folder')
@click.argument('output_directory')
@click.option('--min-duration', default=60, help='Minimum duration in seconds (default: 60)')
@click.option('--max-duration', default=120, help='Maximum duration in seconds (default: 120)')
@click.option('--extensions', default='mp4,avi,mov,mkv', help='Video file extensions to process (comma-separated)')
def remix(input_folder, output_directory, min_duration, max_duration, extensions):
    """Create a video from random segments with speed variations and overlap prevention."""
    input_folder = Path(input_folder).resolve()

    if not input_folder.exists():
        click.echo(f"Error: Input folder does not exist: {input_folder}", err=True)
        return

    # Parse extensions
    video_extensions = tuple(f'.{ext.strip().lower()}' for ext in extensions.split(','))

    # Find video files
    input_videos = [
        str(f) for f in input_folder.glob('*')
        if f.suffix.lower() in video_extensions
    ]

    if not input_videos:
        click.echo(f"Error: No video files found in {input_folder}", err=True)
        return

    click.echo(f"Found {len(input_videos)} video files:")
    for video in input_videos:
        click.echo(f"  - {Path(video).name}")

    click.echo(f"Target duration: {min_duration}-{max_duration} seconds")
    click.echo(f"Output directory: {output_directory}")

    try:
        # Setup logging for the processor
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('./logs/remix.log', encoding='utf-8')
            ],
            force=True
        )
        os.makedirs('./logs', exist_ok=True)

        processor = VideoProcessor((min_duration, max_duration))
        output_file = processor.create_video(input_videos, output_directory)
        click.echo(f"Successfully created remix video: {output_file}")

    except Exception as e:
        click.echo(f"Error creating remix video: {str(e)}", err=True)

@cli.command()
@click.option('--config', '-c', required=True, help='Path to JSON configuration file')
def generate(config):
    """Generate video from configuration file."""
    logger = setup_logging()
    set_imagemagick_path()

    try:
        with open(config, "r", encoding="utf-8") as config_file:
            config_data = json.load(config_file)

        if "videos" in config_data:
            for i, video_config in enumerate(config_data["videos"], 1):
                repeat = video_config.get("repeat", 1)
                for j in range(repeat):
                    edit_video(video_config, logger, j + 1)
        else:
            edit_video(config_data, logger)

    except Exception as e:
        logger.error(f"Error processing JSON configuration: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('directory')
@click.argument('index', type=int)
@click.option('--dry-run', is_flag=True, help='Show what would be done without actually moving files')
def tidy(directory, index, dry_run):
    """Organize files in directory by splitting filename on '_' and using INDEX part."""
    if not os.path.exists(directory):
        click.echo(f"Error: Directory '{directory}' does not exist.", err=True)
        return

    def path(dr, f):
        return os.path.join(dr, f)

    moved_count = 0

    for f in os.listdir(directory):
        fsrc = path(directory, f)
        if os.path.isfile(fsrc):
            parts = f.split("_")
            click.echo(f"File: {f} -> Parts: {parts}")

            if len(parts) > index:
                s = parts[index]
                target_dir = s.upper() if s.isalnum() else "#"
                target = path(directory, target_dir)

                if dry_run:
                    click.echo(f"Would move: {fsrc} -> {path(target, f)}")
                else:
                    if not os.path.exists(target):
                        os.makedirs(target)
                        click.echo(f"Created directory: {target}")

                    shutil.move(fsrc, path(target, f))
                    click.echo(f"Moved: {f} -> {target_dir}/")
                    moved_count += 1
            else:
                click.echo(f"Warning: File '{f}' doesn't have enough parts (index {index})")

    if not dry_run:
        click.echo(f"Successfully moved {moved_count} files.")

@cli.command()
@click.argument('video_file')
@click.argument('playlist_file')
@click.option('--output', '-o', help='Output filename (default: auto-generated)')
@click.option('--codec', default='libx264', help='Video codec')
@click.option('--quality', default='24', help='Video quality (CRF value)')
@click.option('--preset', default='veryfast', help='Encoding preset')
@click.option('--fps', default=24, help='Output FPS')
@click.option('--threads', default=4, help='Number of encoding threads')
def bookmarks(video_file, playlist_file, output, codec, quality, preset, fps, threads):
    """Edit video using bookmark times from XSPF playlist file."""
    if not os.path.exists(video_file):
        click.echo(f"Error: Video file '{video_file}' not found.", err=True)
        return

    if not os.path.exists(playlist_file):
        click.echo(f"Error: Playlist file '{playlist_file}' not found.", err=True)
        return

    # Generate output filename if not provided
    if not output:
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        output = f"./src/edited_{base_name}_.mp4"

    try:
        # Read the XSPF file
        with open(playlist_file, 'r', encoding="utf-8") as f:
            data = f.read()

        # Extract bookmark times using regex
        times = re.findall(r'time=([\d.]+)', data)

        # Create tuples of two bookmark times each
        cuts = list(batched(times, 2)) if hasattr(__builtins__, 'batched') else [(times[i], times[i+1]) for i in range(0, len(times), 2)]

        click.echo(f"Found {len(cuts)} cuts: {cuts}")

        # Load and process video
        video = mpy.VideoFileClip(video_file)

        # Remove duplicates and create clips
        unique_cuts = list(set(cuts))
        clips = [video.subclip(float(cut[0]), float(cut[1])) for cut in unique_cuts]

        # Concatenate clips
        final_clip = mpy.concatenate_videoclips(clips)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else '.', exist_ok=True)

        # Write video file
        click.echo(f"Writing to: {output}")
        final_clip.write_videofile(
            output,
            threads=threads,
            fps=fps,
            codec=codec,
            preset=preset,
            ffmpeg_params=["-crf", quality]
        )

        video.close()
        final_clip.close()

        click.echo("Video processing completed successfully!")

    except Exception as e:
        click.echo(f"Error processing video: {str(e)}", err=True)

@cli.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--top', '-t', default=30, help='Height of top black bar (default: 30px)')
@click.option('--bottom', '-b', default=30, help='Height of bottom black bar (default: 30px)')
@click.option('--cut-start', '-s', default=0.0, help='Duration to cut from beginning in seconds')
@click.option('--cut-end', '-e', default=0.0, help='Duration to cut from end in seconds')
def letterbox(input_file, output_file, top, bottom, cut_start, cut_end):
    """Add black bars to video and optionally trim from start/end."""
    if not os.path.exists(input_file):
        click.echo(f"Error: Input file '{input_file}' not found.", err=True)
        return

    try:
        click.echo(f"Processing video: {input_file}")
        click.echo(f"Output file: {output_file}")
        click.echo(f"Adding {top}px top bar and {bottom}px bottom bar")
        click.echo(f"Cutting {cut_start}s from start and {cut_end}s from end")

        # Load the video file
        video = VideoFileClip(input_file)

        # Cut the specified duration from the beginning and end
        if cut_start > 0 or cut_end > 0:
            start = cut_start
            end = video.duration - cut_end if cut_end > 0 else None
            video = video.subclip(start, end)

        # Get the dimensions
        width, height = video.size

        # Create black bars
        top_bar = ColorClip(size=(width, top), color=(0,0,0)).set_duration(video.duration)
        bottom_bar = ColorClip(size=(width, bottom), color=(0,0,0)).set_duration(video.duration)

        # Position the bars
        top_bar = top_bar.set_position(('center', 'top'))
        bottom_bar = bottom_bar.set_position(('center', 'bottom'))

        # Create the final composite
        final_video = CompositeVideoClip([video, top_bar, bottom_bar])
        final_video = final_video.set_duration(video.duration)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)

        # Write the result
        final_video.write_videofile(
            output_file,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        # Cleanup
        video.close()
        final_video.close()

        click.echo("Video processing completed successfully!")

    except Exception as e:
        click.echo(f"Error processing video: {str(e)}", err=True)

if __name__ == "__main__":
    cli()
