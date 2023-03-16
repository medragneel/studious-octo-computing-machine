# ffmpeg -i ../src/chainsaw.mkv -c copy -map 0 -segment_time 00:00:10 -f segment -reset_timestamps 1 short_%3d.mkv

import subprocess
import sys

try:
    output = subprocess.run(['ffmpeg', '-i', sys.argv[1], '-c', 'copy', '-map', '0', '-segment_time', sys.argv[2], '-f', 'segment', '-reset_timestamps', '1', 'shorts/short%3d.mp4'], check=True, capture_output=True, text=True)
    print(output.stdout)
except subprocess.CalledProcessError as e:
    print(e.stderr)

