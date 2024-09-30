import argparse
import moviepy.editor as mpy
from moviepy.video.fx.all import rotate, speedx
from moviepy.audio.fx.all import audio_fadeout, audio_fadein
from datetime import datetime
from Utils.util import detect_overlapping_tuples, getrandomDuration
import os
from concurrent.futures import ThreadPoolExecutor


def parse_arguments():
    parser = argparse.ArgumentParser(description="Video editing script")
    parser.add_argument("input_video", help="Path to the input video file")
    parser.add_argument("music", help="Path to the music file")
    parser.add_argument(
        "-c", "--cycle", type=int, default=4, help="Number of cuts to make (default: 4)"
    )
    parser.add_argument(
        "-nr",
        "--no-rotate",
        action="store_true",
        help="Disable rotation (default: rotate 270 degrees)",
    )
    parser.add_argument(
        "-s",
        "--speed",
        type=float,
        default=1.2,
        help="Video speed multiplier (default: 1.2)",
    )
    parser.add_argument(
        "-o", "--output", default="", help="Output file name (default: auto-generated)"
    )
    parser.add_argument(
        "-l",
        "--logo-text",
        default="UTOPIA",
        help="Text to display as logo (default: UTOPIA)",
    )
    parser.add_argument(
        "-f",
        "--font",
        default="./fonts/Anurati-Regular.otf",
        help="Font file for logo text",
    )
    parser.add_argument(
        "-re",
        "--repeat",
        type=int,
        default=1,
        help="Number of times to repeat the video generation (default: 1)",
    )
    return parser.parse_args()


def generate_cuts(video, cycle, length):
    while True:
        cuts = [getrandomDuration(video.duration, length) for _ in range(cycle)]
        cts = list({tuple(cut): None for cut in cuts}.keys())
        if not detect_overlapping_tuples(cts):
            break
    return cts


def process_clip(video, cut):
    return video.subclip(cut[0], cut[1]).crossfadein(1)


def edit_video(args, iteration=1):
    if not os.path.exists(args.input_video):
        print(f"Error: Input video file '{args.input_video}' not found.")
        return
    if not os.path.exists(args.music):
        print(f"Error: Music file '{args.music}' not found.")
        return

    video = mpy.VideoFileClip(args.input_video, audio=False)  # Load without audio
    cts = generate_cuts(video, args.cycle, 5)

    # Process clips in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        clips = list(
            filter(None, executor.map(lambda cut: process_clip(video, cut), cts))
        )

    final_clip = mpy.concatenate_videoclips(clips, method="compose").fx(
        speedx, args.speed
    )

    if not args.no_rotate:
        final_clip = final_clip.fx(rotate, 270)

    audio = mpy.AudioFileClip(args.music)
    new_audioclip = mpy.CompositeAudioClip([audio])
    new_audioclip = new_audioclip.set_duration(final_clip.duration)
    new_audioclip = new_audioclip.fx(audio_fadein, duration=2.0)
    new_audioclip = new_audioclip.fx(audio_fadeout, duration=1.0)
    final_clip = final_clip.set_audio(new_audioclip)

    logo = (
        mpy.TextClip(args.logo_text, fontsize=30, color="white", font=args.font)
        .set_position((60, 60))
        .set_opacity(0.7)
        .set_duration(final_clip.duration)
    )

    final = mpy.CompositeVideoClip([final_clip, logo])
    final = final.set_fps(30)

    if not args.output:
        dt = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"./dist/final_{dt}_{iteration}.mp4"
    else:
        name, ext = os.path.splitext(args.output)
        output_filename = f"{name}_{iteration}{ext}"

    final.write_videofile(
        output_filename,
        threads=6,
        fps=30,
        codec="libx264",
        preset="ultrafast",
        ffmpeg_params=["-crf", "30"],
        audio_codec="aac",
    )

    video.close()


if __name__ == "__main__":
    args = parse_arguments()
    try:
        for i in range(args.repeat):
            edit_video(args, i + 1)
    except KeyboardInterrupt:
        print("Process interrupted by user. Shutting down...")
    finally:
        # Perform any necessary cleanup here
        pass
