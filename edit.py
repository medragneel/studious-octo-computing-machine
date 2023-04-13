import moviepy.editor as mpy
from moviepy.video.tools.subtitles import SubtitlesClip
# from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.speedx import speedx
# from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_fadein import audio_fadein
from datetime import datetime
import random
import sys


font_family =  './fonts/Painted Lady.otf'
subs='./ads.srt'

vcodec =   "libx264"

videoquality = "24"

# slow, ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
compression = "superfast"

music = sys.argv[2]
title = sys.argv[1]
dt = datetime.now().strftime("%Y%m%d%H:%M:%S").replace(":","_")
savetitle = f"./dist/final_{dt}_.mp4"
length = 5
cycle = 7


def getrandomDuration(duration):
    start = round(random.uniform(0,duration-length), 1)
    end = start + length
    return start,end

cuts = []

def edit_video(loadtitle, savetitle, cuts):
    # load file
    video = mpy.VideoFileClip(loadtitle,audio=True)
    #list of random cuts
    for _ in range(cycle):
        cuts.append(getrandomDuration(video.duration))
    # a set to remove duplicate
    cts = set(cuts)
    print(cuts)

    #list of clips
    clips = [ video.subclip(cut[0],cut[1]) for cut in cts]

    #final clip

    final_clip = mpy.concatenate_videoclips(clips)\
          .fx(speedx,1.2)\
          .fx(rotate,270)\
          # .fx(blackwhite,preserve_luminosity=True)\
        # .fx(lum_contrast,lum=1.1,contrast =0.5)\

    # add audio to clips
    audio = mpy.AudioFileClip(music)

    new_audioclip = mpy.CompositeAudioClip([audio])
    final_clip.audio = new_audioclip.set_duration(final_clip.duration)
    final_clip.audio = new_audioclip.fx(audio_fadein, duration=2.0)
    final_clip.audio = new_audioclip.fx(audio_fadeout, duration=1.0)


    logo = mpy.TextClip("Utopia", fontsize=30, color='white', font=font_family)\
            .set_position((40,40))\
            .set_opacity(0.7)\
            .set_duration(final_clip.duration)

    # intro = mpy.TextClip("Utopia", fontsize=90, color='white', font=font_family)\
    #         .set_position(('center','center'))\
    #         .set_opacity(0.7)\
    #         .set_duration(1.0)\
    #         .rotate(10)

    # generator = lambda txt: mpy.TextClip(txt, \
    #                              font ="./fonts/roboto.ttf", \
    #                              fontsize=18,\
    #                               color='white', \
    #                               # kerning=2,\
    #                               # interline=8,\
    #                               )
    # print(generator)
    #
    #
    # subtitles = SubtitlesClip(subs,generator).set_position(('center','center'))
    #
    # final = mpy.CompositeVideoClip([final_clip,logo,subtitles])
    final = mpy.CompositeVideoClip([final_clip,logo])






    # # save file
    final.write_videofile(savetitle,
                               threads=4,
                               fps=24,
                               codec=vcodec,
                               preset=compression,
                               ffmpeg_params=["-crf",videoquality])

    video.close()


if __name__ == '__main__':
    edit_video(title, savetitle, cuts)
