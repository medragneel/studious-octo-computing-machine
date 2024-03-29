import csv
import moviepy.editor as mpy
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.speedx import speedx
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_fadein import audio_fadein
from datetime import datetime
import sys
from utils import detect_overlapping_tuples, getrandomDuration

dataset_file = "./dataset.csv"
font_family = './fonts/Anurati-Regular.otf'
vcodec = "libx264"
videoquality = "30"
compression = "superfast"

music = sys.argv[2]
title = sys.argv[1]
dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":", "_")
savetitle = f"./dist/final_{dt}_.mp4"
length = 5
cycle = int(sys.argv[3])

cuts = []



# def generate_and_classify_cuts(video, cycle, length):
#     cuts = []
#
#     for _ in range(cycle):
#         cuts.append(getrandomDuration(video.duration, length))
#
#     # Remove duplicate cuts
#     cts = list({tuple(cut): None for cut in cuts}.keys())
#
#     # Check if all cuts are unique
#     classified = "Unique" if not detect_overlapping_tuples(cts) else "Repeated"
#
#     # List of clips
#     clips = [video.subclip(cut[0], cut[1]).crossfadein(1) for cut in cts]
#
#     return clips, classified, cuts
#
def generate_and_classify_cuts(video, cycle, length):
    while True:
        cuts = [getrandomDuration(video.duration, length) for _ in range(cycle)]

        # Remove duplicate cuts
        cts = list({tuple(cut): None for cut in cuts}.keys())

        # Check if all cuts are unique
        if not detect_overlapping_tuples(cts):
            classified = "Unique"
            break
        else:
            classified = "Repeated"

    # List of clips
    clips = [video.subclip(cut[0], cut[1]).crossfadein(1) for cut in cts]

    return clips, classified, cuts



def edit_video(loadtitle, savetitle, cuts):
    video = mpy.VideoFileClip(loadtitle, audio=True)

    clips, classified, cuts = generate_and_classify_cuts(video, cycle, length)

    with open('dataset.csv', "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([cuts, classified])



    # Final clip
    if sys.argv[4] == "r":
        final_clip = mpy.concatenate_videoclips(clips, method="compose")\
            .fx(speedx, 1.2)\
            .fx(rotate, 270)

        audio = mpy.AudioFileClip(music)
        new_audioclip = mpy.CompositeAudioClip([audio])
        final_clip.audio = new_audioclip.set_duration(final_clip.duration)
        final_clip.audio = new_audioclip.fx(audio_fadein, duration=2.0)
        final_clip.audio = new_audioclip.fx(audio_fadeout, duration=1.0)

        logo = mpy.TextClip("UTOPIA", fontsize=30, color='white', font=font_family)\
            .set_position((60, 60))\
            .set_opacity(0.7)\
            .set_duration(final_clip.duration)

        final = mpy.CompositeVideoClip([final_clip, logo])
        final.set_fps(30)

        final.write_videofile(savetitle,
                              threads=6,
                              fps=30,
                              codec=vcodec,
                              preset=compression,
                              ffmpeg_params=["-crf", videoquality])
    else:
        final_clip = mpy.concatenate_videoclips(clips, method="compose")\
            .fx(speedx, 1.2)

        audio = mpy.AudioFileClip(music)
        new_audioclip = mpy.CompositeAudioClip([audio])
        final_clip.audio = new_audioclip.set_duration(final_clip.duration)
        final_clip.audio = new_audioclip.fx(audio_fadein, duration=2.0)
        final_clip.audio = new_audioclip.fx(audio_fadeout, duration=1.0)

        logo = mpy.TextClip("UTOPIA", fontsize=30, color='white', font=font_family)\
            .set_position((60, 60))\
            .set_opacity(0.7)\
            .set_duration(final_clip.duration)

        final = mpy.CompositeVideoClip([final_clip, logo])
        final.set_fps(30)

        final.write_videofile(savetitle,
                              threads=6,
                              fps=30,
                              codec=vcodec,
                              preset=compression,
                              ffmpeg_params=["-crf", videoquality])

    video.close()


if __name__ == '__main__':
    edit_video(title, savetitle, cuts)
