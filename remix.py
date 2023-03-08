# ffmpeg -i input.mp3 -filter:a "atempo=1.5" output.mp3
# ffmpeg -i test.mp3 -af asetrate=44100*0.9,aresample=44100,atempo=1/0.9 output.mp3

import subprocess
import sys

try:
    output = subprocess.run(['ffmpeg', '-i', sys.argv[1], '-af', f'asetrate={sys.argv[3]}*{int(float(sys.argv[2]))},aresample={sys.argv[3]},atempo={1/float(sys.argv[2])}', sys.argv[4]], check=True, capture_output=True, text=True)
    print(output.stdout)
except subprocess.CalledProcessError as e:
    print(e.stderr)
