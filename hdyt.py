import os
import subprocess
import time
import random
from pytube import YouTube

def download_video(url, output_path="."):
    try:
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.youtube.com/',
            'Connection': 'keep-alive'
        }
        
        # Create a YouTube object with additional options to work around API changes
        yt = YouTube(
            url,
            use_oauth=False,
            allow_oauth_cache=True
        )
        
        # Apply headers to the request session
        for key, value in headers.items():
            yt.http_client.session.headers[key] = value
            
        # Short delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))

        print(f"Fetching available streams for: {yt.title}")
        
        # Get the highest resolution stream (video only)
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', type="video").order_by('resolution').desc().first()

        # Get the audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()

        if video_stream and audio_stream:
            print(f"Video resolution selected: {video_stream.resolution}")
            print(f"Audio itag selected: {audio_stream.itag}")

            # Create safe filename
            safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c in ' ._-']).rstrip()
            
            # Download video with a short delay between requests
            print("Downloading video stream...")
            video_file = video_stream.download(output_path, filename=f"video_temp.mp4")
            time.sleep(random.uniform(1, 2))
            
            # Download audio
            print("Downloading audio stream...")
            audio_file = audio_stream.download(output_path, filename=f"audio_temp.mp4")

            # Combine video and audio using FFmpeg
            output_file = os.path.join(output_path, f"{safe_title}.mp4")
            
            # Make sure the output file doesn't already exist
            counter = 1
            original_output = output_file
            while os.path.exists(output_file):
                output_file = original_output.replace(".mp4", f"_{counter}.mp4")
                counter += 1
            
            print("Merging video and audio...")
            ffmpeg_command = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{output_file}" -y'
            subprocess.call(ffmpeg_command, shell=True)

            # Remove temporary files
            if os.path.exists(video_file):
                os.remove(video_file)
            if os.path.exists(audio_file):
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
        if "403" in str(e) or "Forbidden" in str(e):
            print("\nTroubleshooting for 403 Forbidden error:")
            print("1. YouTube may be blocking your requests due to rate limiting or IP detection.")
            print("2. Try using a VPN or waiting a while before trying again.")
            print("3. The pytube library might need to be updated to handle new YouTube changes.")
            print("4. As an alternative, try using yt-dlp instead of pytube (pip install yt-dlp).")
        elif "regex_search" in str(e) or "cipher" in str(e).lower():
            print("\nTroubleshooting advice: YouTube may have changed their cipher algorithm.")
            print("Try upgrading pytube: pip install --upgrade pytube")
            print("Or consider switching to yt-dlp: pip install yt-dlp")
        elif "age" in str(e).lower() and "restricted" in str(e).lower():
            print("\nTroubleshooting advice: This video might be age-restricted.")
            print("Age-restricted videos might require additional authentication.")

def use_yt_dlp(url, output_path="."):
    """Alternative implementation using yt-dlp which is more robust"""
    try:
        # Create a safe output directory path for command
        if " " in output_path:
            output_path = f'"{output_path}"'
            
        # Format the command for yt-dlp
        cmd = f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o {output_path}/%(title)s.%(ext)s {url}'
        
        print("Attempting download with yt-dlp...")
        subprocess.call(cmd, shell=True)
        print("Download complete!")
    except Exception as e:
        print(f"yt-dlp error: {str(e)}")
        print("Please ensure yt-dlp is installed: pip install yt-dlp")

if __name__ == "__main__":
    # Get user input for the YouTube video URL
    video_url = input("Enter the YouTube video URL: ")

    # Get user input for the output directory (optional)
    output_dir = input("Enter the output directory (press Enter for current directory): ").strip()
    if not output_dir:
        output_dir = "."

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # First ask if user wants to try pytube or go straight to yt-dlp
    choice = input("Would you like to try (1) pytube or (2) yt-dlp? (1/2, default=1): ").strip()
    
    if choice == "2":
        # Check if yt-dlp is installed
        try:
            subprocess.run(["yt-dlp", "--version"], check=True, capture_output=True)
            use_yt_dlp(video_url, output_dir)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("yt-dlp is not installed. Attempting to install it...")
            subprocess.call("pip install yt-dlp", shell=True)
            print("Now trying download with yt-dlp...")
            use_yt_dlp(video_url, output_dir)
    else:
        # Try using pytube
        print("Checking pytube version...")
        try:
            subprocess.call("pip install --upgrade pytube", shell=True)
            print("pytube updated to latest version")
        except:
            print("Could not automatically update pytube.")
            
        # Download the video
        download_video(video_url, output_dir)