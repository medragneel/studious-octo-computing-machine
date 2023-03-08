import moviepy.editor
import os
import random
import fnmatch
from datetime import datetime

directory = './shorts'
ext = "*mp4"
length = 10
vcodec =   "libx264"

videoquality = "24"

# slow, ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
compression = "fast"

dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":","")
out = "./exported/exported_" + dt + "_.mp4"

def getrandomDuration(duration):
    start = round(random.uniform(0,duration-length), 2)
    end = start + length
    return start,end

# outputs=[]
clips = []

# compile list of videos
inputs = [os.path.join(directory,f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and fnmatch.fnmatch(f, ext)]
print(inputs)

for i in inputs:

    # import to moviepy
    video = moviepy.editor.VideoFileClip(i)
    outputs = [getrandomDuration(video.duration) for _ in range(30)]
    # for _ in range(30):
    #     duration = getrandomDuration(video.duration)
    #     outputs.append(duration)
    print(outputs)

    for cut in outputs:
        clip = video.subclip(cut[0],cut[1])
        clips.append(clip)

collage = moviepy.editor.concatenate_videoclips(clips)

collage.write_videofile(out, threads=4, fps=24,
                               codec=vcodec,
                               preset=compression,
                               ffmpeg_params=["-crf",videoquality])

# collage.write_videofile(out)
