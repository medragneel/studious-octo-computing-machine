import argparse
import json
import moviepy.editor as mpy
from moviepy.video.fx.all import rotate, speedx
from moviepy.audio.fx.all import audio_fadeout, audio_fadein
from datetime import datetime
from Utils.util import detect_overlapping_tuples, getrandomDuration
import os
from concurrent.futures import ThreadPoolExecutor


def parse_arguments():
    parser = argparse.ArgumentParser(description="Video editing script")
    parser.add_argument(
        "--config", help="Path to JSON configuration file", required=True
    )
    return parser.parse_args()


def load_config(config_file):
    with open(config_file, "r") as f:
        return json.load(f)


def generate_cuts(video, cycle, length):
    while True:
        cuts = [getrandomDuration(video.duration, length) for _ in range(cycle)]
        cts = list({tuple(cut): None for cut in cuts}.keys())
        if not detect_overlapping_tuples(cts):
            break
    return cts


def process_clip(video, cut):
    return video.subclip(cut[0], cut[1]).crossfadein(1)


def edit_video(video_config, itr=1):
    # Required fields
    input_video = video_config.get("input_video")
    music = video_config.get("music")
    if not input_video or not music:
        raise ValueError(
            "'input_video' and 'music' are required fields in the configuration."
        )

    # Optional fields with default values
    cycle = video_config.get("cycle", 4)
    no_rotate = video_config.get("no_rotate", False)
    speed = video_config.get("speed", 1.2)
    output = video_config.get("output", "")
    logo_text = video_config.get("logo_text", "UTOPIA")
    font = video_config.get("font", "./fonts/Anurati-Regular.otf")

    video = mpy.VideoFileClip(input_video, audio=False)  # Load without audio
    cts = generate_cuts(video, cycle, 5)  # 5 is hardcoded length

    # Process clips in parallel
    with ThreadPoolExecutor() as executor:
        clips = list(executor.map(lambda cut: process_clip(video, cut), cts))

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

    if not output:
        dt = datetime.now().strftime("%Y%m%d%H%M%S")
        output = f"./dist/final_{dt}_.mp4"
    else:
        name, ext = os.path.splitext(output)
        output = f"{name}_{itr}{ext}"

    final.write_videofile(
        output,
        threads=6,
        fps=30,
        codec="libx264",
        preset="ultrafast",
        ffmpeg_params=["-crf", "30"],
        audio_codec="aac",
    )

    video.close()


def process_videos(config):
    for i, video_config in enumerate(config["videos"], 1):
        repeat = video_config.get("repeat", 1)
        print(f"Processing video {i}: {video_config.get('input_video', 'Unknown')}")
        for j in range(repeat):
            try:
                edit_video(video_config, j + 1)
                print(f"Finished processing video {i}, iteration {j+1}")
            except Exception as e:
                print(f"Error processing video {i}, iteration {j+1}: {str(e)}")


if __name__ == "__main__":
    args = parse_arguments()
    config = load_config(args.config)
    process_videos(config)
