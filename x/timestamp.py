import re
import moviepy.editor as mpy
import sys
import os




vcodec =   "libx264"

videoquality = "24"

# slow, ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
compression = "veryfast"

title = sys.argv[1]
savetitle = f"./src/edited_{os.path.splitext(os.path.basename(title))[0]}_.mp4"

# read the XSPF file into a string
with open(sys.argv[2], 'r') as f:
    data = f.read()

# use regular expressions to extract the bookmark times
times = re.findall(r'time=([\d.]+)', data)

# create tuples of two bookmark times each
cuts = []
for i in range(0, len(times), 2):
    cuts.append((times[i], times[i+1]))

# print the bookmark tuples
print(cuts)


def edit_video(loadtitle, savetitle, cuts):
    # load file
    video = mpy.VideoFileClip(loadtitle)
    # a set to remove duplicate
    cts = set(cuts)
    print(cuts)

    #list of clips
    clips = [ video.subclip(cut[0],cut[1]) for cut in cts]

    #final clip
    final_clip = mpy.concatenate_videoclips(clips)\





    # # save file
    final_clip.write_videofile(savetitle,
                               threads=4,
                               fps=24,
                               codec=vcodec,
                               preset=compression,
                               ffmpeg_params=["-crf",videoquality])

    video.close()


if __name__ == '__main__':
    edit_video(title, savetitle, cuts)
