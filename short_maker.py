import os
import random
import subprocess
from datetime import datetime

# Set the path to the folder containing the videos
path_to_folder = "./shorts"
dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":","_")
savetitle = f"./exported/short_{dt}_.mp4"

# Get a list of all the videos in the folder
videos = [os.path.join(path_to_folder, f) for f in os.listdir(path_to_folder) if f.endswith('.mp4')]

# Shuffle the list of videos randomly
random.shuffle(videos)


# Use ffmpeg to concatenate the videos into a single output video
cmd = ['ffmpeg', '-y']
for video in videos:
    cmd.extend(['-i', video])
cmd.extend(['-filter_complex', 'concat=n={}:v=1:a=1'.format(len(videos)), '-vcodec', 'libx264', '-preset', 'ultrafast', '-crf', '23', savetitle])
subprocess.run(cmd, check=True)

print("Video concatenation complete!")

