from pathlib import Path
from datetime import datetime


import datetime

def reformat_timestamp(timestamp):
    # Convert the timestamp to a datetime object
    dt_object = datetime.datetime.fromtimestamp(timestamp)

    # Format the datetime object into a human-readable string
    formatted_timestamp = dt_object.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_timestamp

files= Path("./src/")


for f in files.iterdir():
    parent = f.parent
    ext = f.suffix
    old = f.stat().st_mtime
    print(reformat_timestamp(old))




