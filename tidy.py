import os
import sys
import shutil

index=0

def path(dr, f): return os.path.join(dr, f)

dr = sys.argv[1]
for f in os.listdir(dr):
    fsrc = path(dr, f)
    if os.path.isfile(fsrc):
        print(f.split("_"))
        s = f.split("_")[index]; target = path(dr, s.upper()) if s.isalnum() else path(dr, "#")
        if not os.path.exists(target):
            os.mkdir(target)
        shutil.move(fsrc, path(target, f))
