import speech_recognition as sr
from pydub import AudioSegment
import datetime
import sys

# Load the audio file
sound = AudioSegment.from_wav(sys.argv[1])

# Set the duration of each subtitle in seconds
subtitle_duration = 1

# Set the minimum length of each subtitle in characters
min_subtitle_length = 1

# Initialize the recognizer
r = sr.Recognizer()

# Loop through the audio in chunks of the specified duration
for i, chunk in enumerate(sound[::subtitle_duration * 1000]):
    print(chunk)

    # Convert the audio chunk to an audio file
    chunk.export("chunk.wav", format="wav")

    # Transcribe the audio chunk using the recognizer
    with sr.AudioFile("chunk.wav") as source:
        audio = r.record(source)
        try:
            text = r.recognize_google(audio)
            # Only create a subtitle if the text is long enough
            if len(text) > min_subtitle_length:
                start_time = datetime.timedelta(seconds=i * subtitle_duration)
                end_time = datetime.timedelta(seconds=(i + 1) * subtitle_duration)
                subtitle_text = text.replace('\n', ' ').replace('\r', '')
                subtitle = f"{i+1}\n{start_time},000 -->  {end_time},000\n{subtitle_text}\n\n"
                with open(sys.argv[2], "a") as f:
                    f.write(subtitle)
        except sr.UnknownValueError:
            pass

