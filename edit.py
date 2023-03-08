import moviepy.editor as mpy
import moviepy.video.fx.all as vfx
from datetime import datetime
import random
import sys



vcodec =   "libx264"

videoquality = "24"

# slow, ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
compression = "veryfast"

music = sys.argv[2]
title = sys.argv[1]
dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":","_")
savetitle = f"./dist/final_{dt}_.mp4"

# modify these start and end times for your subclips
# cuts = [('00:00:10.949', '00:00:20.152'),
#         ('00:02:06.328', '00:02:13.077') ,
#         ('00:03:06.328', '00:03:13.077') ,
#         ('00:05:06.328', '00:05:13.077') ,
#         ('00:04:06.328', '00:04:13.077') ,
#         ]


length = 5
cycle = 29

def getrandomDuration(duration):
    start = round(random.uniform(0,duration-length), 2)
    end = start + length
    return start,end


# Define a function to apply a random effect to the clip


cuts = []

def edit_video(loadtitle, savetitle, cuts):
    # load file
    video = mpy.VideoFileClip(loadtitle)
    #list of random cuts
    for _ in range(cycle):
        cuts.append(getrandomDuration(video.duration))
    # a set to remove duplicate
    cts = set(cuts)
    print(cuts)

    #list of clips
    clips = [ video.subclip(cut[0],cut[1]) for cut in cts]

    #final clip
    final_clip = mpy.concatenate_videoclips(clips)
    # add audio to clips
    audio = mpy.AudioFileClip(music)

    new_audioclip = mpy.CompositeAudioClip([audio])
    final_clip.audio = new_audioclip.set_duration(final_clip.duration)


    # save file
    final_clip.write_videofile(savetitle,
                               threads=4,
                               fps=24,
                               bitrate="5000k",
                               codec=vcodec,
                               preset=compression,
                               ffmpeg_params=["-crf",videoquality])

    video.close()


if __name__ == '__main__':
    edit_video(title, savetitle, cuts)
