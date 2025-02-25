import os
import subprocess
from pytube import YouTube

def download_video(url, output_path="."):
    try:
        # Create a YouTube object with additional options to work around API changes
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True
        )

        # Get the highest resolution stream (video only)
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', type="video").order_by('resolution').desc().first()

        # Get the audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()

        if video_stream and audio_stream:
            print(f"Downloading: {yt.title}")
            print(f"Video resolution: {video_stream.resolution}")

            # Create safe filename
            safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c in ' ._-']).rstrip()
            
            # Download video
            video_file = video_stream.download(output_path, filename=f"video_temp.mp4")
            
            # Download audio
            audio_file = audio_stream.download(output_path, filename=f"audio_temp.mp4")

            # Combine video and audio using FFmpeg
            output_file = os.path.join(output_path, f"{safe_title}.mp4")
            
            # Make sure the output file doesn't already exist
            counter = 1
            original_output = output_file
            while os.path.exists(output_file):
                output_file = original_output.replace(".mp4", f"_{counter}.mp4")
                counter += 1
            
            ffmpeg_command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}" -y'
            
            print("Merging video and audio...")
            subprocess.call(ffmpeg_command, shell=True)

            # Remove temporary files
            os.remove(video_file)
            os.remove(audio_file)

            print(f"Download and merge complete! File saved as: {output_file}")
        else:
            print("Couldn't find suitable video and audio streams.")
            print("Available streams:")
            for stream in yt.streams:
                print(f" - {stream}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        # Additional troubleshooting for common pytube issues
        if "regex_search" in str(e):
            print("\nTroubleshooting advice: The pytube library might be outdated.")
            print("Try updating pytube with: pip install --upgrade pytube")
        elif "cipher" in str(e).lower():
            print("\nTroubleshooting advice: YouTube may have changed their cipher algorithm.")
            print("Try updating pytube with: pip install --upgrade pytube")
        elif "age" in str(e).lower() and "restricted" in str(e).lower():
            print("\nTroubleshooting advice: This video might be age-restricted.")
            print("Age-restricted videos might require additional authentication.")

if __name__ == "__main__":
    # Get user input for the YouTube video URL
    video_url = input("Enter the YouTube video URL: ")

    # Get user input for the output directory (optional)
    output_dir = input("Enter the output directory (press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # First ensure pytube is up to date
    print("Checking pytube version...")
    try:
        subprocess.call("pip install --upgrade pytube", shell=True)
        print("pytube updated to latest version")
    except:
        print("Could not automatically update pytube. If issues persist, run: pip install --upgrade pytube")

    # Download the video
    download_video(video_url, output_dir)
