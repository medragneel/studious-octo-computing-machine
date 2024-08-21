import argparse
import csv
import moviepy.editor as mpy
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.speedx import speedx
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_fadein import audio_fadein
from datetime import datetime
from utils import detect_overlapping_tuples, getrandomDuration

def parse_arguments():
    parser = argparse.ArgumentParser(description="Video editing script")
    parser.add_argument("input_video", help="Path to the input video file")
    parser.add_argument("music", help="Path to the music file")
    parser.add_argument("-c", "--cycle", type=int, default=4, help="Number of cuts to make (default: 4)")
    parser.add_argument("-nr", "--no-rotate", action="store_true", help="Disable rotation (default: rotate 270 degrees)")
    parser.add_argument("-s", "--speed", type=float, default=1.2, help="Video speed multiplier (default: 1.2)")
    parser.add_argument("-o", "--output", default="", help="Output file name (default: auto-generated)")
    parser.add_argument("-l", "--logo-text", default="UTOPIA", help="Text to display as logo (default: UTOPIA)")
    parser.add_argument("-f", "--font", default='./fonts/Anurati-Regular.otf', help="Font file for logo text")
    return parser.parse_args()

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

def edit_video(args):
    video = mpy.VideoFileClip(args.input_video, audio=True)
    clips, classified, cuts = generate_and_classify_cuts(video, args.cycle, 5)  # 5 is hardcoded length

    with open('dataset.csv', "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([cuts, classified])

    final_clip = mpy.concatenate_videoclips(clips, method="compose").fx(speedx, args.speed)

    if not args.no_rotate:
        final_clip = final_clip.fx(rotate, 270)

    audio = mpy.AudioFileClip(args.music)
    new_audioclip = mpy.CompositeAudioClip([audio])
    final_clip.audio = new_audioclip.set_duration(final_clip.duration)
    final_clip.audio = new_audioclip.fx(audio_fadein, duration=2.0)
    final_clip.audio = new_audioclip.fx(audio_fadeout, duration=1.0)

    logo = mpy.TextClip(args.logo_text, fontsize=30, color='white', font=args.font)\
        .set_position((60, 60))\
        .set_opacity(0.7)\
        .set_duration(final_clip.duration)

    final = mpy.CompositeVideoClip([final_clip, logo])
    final.set_fps(30)

    if not args.output:
        dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":", "_")
        args.output = f"./dist/final_{dt}_.mp4"

    final.write_videofile(args.output,
                          threads=6,
                          fps=30,
                          codec="libx264",
                          preset="superfast",
                          ffmpeg_params=["-crf", "30"])

    video.close()

if __name__ == '__main__':
    args = parse_arguments()
    edit_video(args)
