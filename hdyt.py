import os
import subprocess
from pytube import YouTube

def download_video(url, output_path="."):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get the highest resolution stream (video only)
        video_stream = yt.streams.filter(progressive=False, file_extension='mp4').order_by('resolution').desc().first()

        # Get the audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()

        if video_stream and audio_stream:
            print(f"Downloading: {yt.title}")
            print(f"Video resolution: {video_stream.resolution}")

            # Download video
            video_file = video_stream.download(output_path, filename_prefix="video_")
            
            # Download audio
            audio_file = audio_stream.download(output_path, filename_prefix="audio_")

            # Combine video and audio using FFmpeg
            output_file = os.path.join(output_path, f"{yt.title}.mp4")
            ffmpeg_command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}"'
            
            print("Merging video and audio...")
            subprocess.call(ffmpeg_command, shell=True)

            # Remove temporary files
            os.remove(video_file)
            os.remove(audio_file)

            print(f"Download and merge complete! File saved as: {output_file}")
        else:
            print("Couldn't find suitable video and audio streams.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Get user input for the YouTube video URL
    video_url = input("Enter the YouTube video URL: ")

    # Get user input for the output directory (optional)
    output_dir = input("Enter the output directory (press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Download the video
    download_video(video_url, output_dir)