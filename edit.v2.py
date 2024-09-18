import argparse
import csv
import json
import moviepy.editor as mpy
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.speedx import speedx
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_fadein import audio_fadein
from datetime import datetime
from utils import detect_overlapping_tuples, getrandomDuration

def parse_arguments():
    parser = argparse.ArgumentParser(description="Video editing script")
    parser.add_argument("--config", help="Path to JSON configuration file", required=True)
    return parser.parse_args()

def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)

def generate_and_classify_cuts(video, cycle, length):
    while True:
        cuts = [getrandomDuration(video.duration, length) for _ in range(cycle)]
        cts = list({tuple(cut): None for cut in cuts}.keys())
        if not detect_overlapping_tuples(cts):
            classified = "Unique"
            break
        else:
            classified = "Repeated"
    clips = [video.subclip(cut[0], cut[1]).crossfadein(1) for cut in cts]
    return clips, classified, cuts

def edit_video(video_config):
    # Required fields
    input_video = video_config.get('input_video')
    music = video_config.get('music')

    if not input_video or not music:
        raise ValueError("'input_video' and 'music' are required fields in the configuration.")

    # Optional fields with default values
    cycle = video_config.get('cycle', 4)
    no_rotate = video_config.get('no_rotate', False)
    speed = video_config.get('speed', 1.2)
    output = video_config.get('output', '')
    logo_text = video_config.get('logo_text', 'UTOPIA')
    font = video_config.get('font', './fonts/Anurati-Regular.otf')

    video = mpy.VideoFileClip(input_video, audio=True)
    clips, classified, cuts = generate_and_classify_cuts(video, cycle, 5)  # 5 is hardcoded length

    with open('dataset.csv', "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([cuts, classified])

    final_clip = mpy.concatenate_videoclips(clips, method="compose").fx(speedx, speed)

    if not no_rotate:
        final_clip = final_clip.fx(rotate, 270)

    audio = mpy.AudioFileClip(music)
    new_audioclip = mpy.CompositeAudioClip([audio])
    final_clip.audio = new_audioclip.set_duration(final_clip.duration)
    final_clip.audio = new_audioclip.fx(audio_fadein, duration=2.0)
    final_clip.audio = new_audioclip.fx(audio_fadeout, duration=1.0)

    logo = mpy.TextClip(logo_text, fontsize=30, color='white', font=font)\
        .set_position((60, 60))\
        .set_opacity(0.7)\
        .set_duration(final_clip.duration)

    final = mpy.CompositeVideoClip([final_clip, logo])
    final.set_fps(30)

    if not output:
        dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":", "_")
        output = f"./dist/final_{dt}_.mp4"

    final.write_videofile(output,
                          threads=6,
                          fps=30,
                          codec="libx264",
                          preset="superfast",
                          ffmpeg_params=["-crf", "30"])

    video.close()

def process_videos(config):
    for i, video_config in enumerate(config['videos'], 1):
        print(f"Processing video {i}: {video_config.get('input_video', 'Unknown')}")
        try:
            edit_video(video_config)
            print(f"Finished processing video {i}")
        except Exception as e:
            print(f"Error processing video {i}: {str(e)}")

if __name__ == '__main__':
    args = parse_arguments()
    config = load_config(args.config)
    process_videos(config)
