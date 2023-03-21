import speech_recognition as sr
import pysrt

# initialize the recognizer
r = sr.Recognizer()


# use the audio file as source

r = sr.Recognizer()
audio_file = sr.AudioFile("./venus [vocals] (1).wav")

with audio_file as source:
    audio = r.record(source)

transcript = r.recognize_google(audio)

srt_file = pysrt.SubRipFile()
srt_file.append(pysrt.SubRipItem(
    index=1,
    start=pysrt.SubRipTime(0, 0, 0, 0),
    end=pysrt.SubRipTime(0, 0, 10, 0),
    text=transcript
))

srt_file.save("venus.srt")

