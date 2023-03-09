import moviepy.editor
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import fnmatch
# from datetime import datetime
# import random


directory = './src'
ext = "*mp4"



inputs = [os.path.join(directory,f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and fnmatch.fnmatch(f, ext)]
print(inputs)

for file in inputs:
    video = moviepy.editor.VideoFileClip(file)
    d = video.duration
    sd = 15
    ct = int(d // sd)
    for i in range(ct):
        start_time = i * sd
        end_time = min((i+1) * sd, d)
        ffmpeg_extract_subclip(file, start_time, end_time, targetname=f"./shorts/seg_{i}.mp4")


