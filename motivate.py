# Import necessary modules
import moviepy.editor as mp
import random
from moviepy.audio.fx.audio_fadeout import audio_fadeout


# Define a list of motivational quotes
quotes = [
    "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "I have not failed. I've just found 10,000 ways that won't work. - Thomas Edison",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "You miss 100% of the shots you don't take. - Wayne Gretzky",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson"
]

# Randomly select a quote from the list
quote = random.choice(quotes)
music = './bb.mp3'
font_family =  './fonts/dash.otf'
vcodec =   "libx264"
videoquality = "24"
compression = "veryfast"

def edit_video(loadtitle, savetitle):
    # load file
    final_clip = mp.VideoFileClip(loadtitle)


    # add audio to clips
    audio = mp.AudioFileClip(music)

    new_audioclip = mp.CompositeAudioClip([audio])
    final_clip.audio = new_audioclip.set_duration(final_clip.duration)
    final_clip.audio = new_audioclip.fx(audio_fadeout, duration=2.0)


    logo = mp.TextClip(quote, fontsize=30, color='white', font=font_family)\
            .set_position(('center','center'))\
            .set_duration(final_clip.duration)

    final = mp.CompositeVideoClip([final_clip,logo])






    # # save file
    final.write_videofile(savetitle,
                               threads=4,
                               fps=24,
                               codec=vcodec,
                               preset=compression,
                               ffmpeg_params=["-crf",videoquality])

    final_clip.close()


if __name__ == '__main__':
    edit_video("./render.mp4", "motivation_clip.mp4")
# Create the text clip with the selected quote
