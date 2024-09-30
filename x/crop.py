import argparse
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
from tqdm import tqdm

def process_video(input_file, output_file, top_height, bottom_height, cut_start, cut_end):
    # Load the video file
    video = VideoFileClip(input_file)

    # Cut the specified duration from the beginning and end
    if cut_start > 0 or cut_end > 0:
        start = cut_start
        end = video.duration - cut_end if cut_end > 0 else None
        video = video.subclip(start, end)

    # Get the dimensions
    width, height = video.size

    # Create black bars
    top_bar = ColorClip(size=(width, top_height), color=(0,0,0)).set_duration(video.duration)
    bottom_bar = ColorClip(size=(width, bottom_height), color=(0,0,0)).set_duration(video.duration)

    # Position the bars
    top_bar = top_bar.set_position(('center', 'top'))
    bottom_bar = bottom_bar.set_position(('center', 'bottom'))

    # Create the final composite
    final_video = CompositeVideoClip([video, top_bar, bottom_bar])

    # Set the duration of the final video
    final_video = final_video.set_duration(video.duration)

    # # Create a progress bar
    # progress_bar = tqdm(total=100, unit='%', desc='Processing')
    #
    # # Function to update progress bar
    # def update_progress(t):
    #     progress = int((t / video.duration) * 100)
    #     progress_bar.n = progress
    #     progress_bar.refresh()
    #
    # Write the result to a file
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True)

    # Close the progress bar
    # progress_bar.close()

    # Close the video clips
    video.close()
    final_video.close()

def main():
    parser = argparse.ArgumentParser(description='Process video: cut from beginning and end, add black bars.')
    parser.add_argument('input', help='Input video file')
    parser.add_argument('output', help='Output video file')
    parser.add_argument('-t','--top', type=int, default=30, help='Height of top black bar (default: 30)')
    parser.add_argument('-b','--bottom', type=int, default=30, help='Height of bottom black bar (default: 30)')
    parser.add_argument('-s','--cut-start', type=float, default=0, help='Duration to cut from the beginning of the video in seconds (default: 10)')
    parser.add_argument('-e','--cut-end', type=float, default=0, help='Duration to cut from the end of the video in seconds (default: 0)')

    args = parser.parse_args()

    print(f"Processing video: {args.input}")
    print(f"Output file: {args.output}")
    print(f"Adding {args.top}px black bar on top and {args.bottom}px black bar on bottom")
    print(f"Cutting the first {args.cut_start} seconds of the video")
    print(f"Cutting the last {args.cut_end} seconds of the video")

    process_video(args.input, args.output, args.top, args.bottom, args.cut_start, args.cut_end)

    print("Video processing completed successfully!")

if __name__ == "__main__":
    main()
