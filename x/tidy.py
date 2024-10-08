import os
import sys
import shutil

index= int(sys.argv[2])

def path(dr, f): return os.path.join(dr, f)

dr = sys.argv[1]
for f in os.listdir(dr):
    fsrc = path(dr, f)
    if os.path.isfile(fsrc):
        print(f.split("_"))
        # for src / dist
        s = f.split("_")[index]; target = path(dr, s.upper()) if s.isalnum() else path(dr, "#")
        # for tracks
        # s = f.split("_")[index].split(".")[0]; target = path(dr, s.upper()) if s.isalnum() else path(dr, "#")
        if not os.path.exists(target):
            os.mkdir(target)
        shutil.move(fsrc, path(target, f))
