import requests
import re

# url = "http://localhost:3000/trending/day/1"
# response = requests.get("http://localhost:3000/tags")  #url for images
# response = requests.get("http://localhost:3000/watch/nikuen-2") #url for videos



pattern = r'https:\/\/m3u8s\.highwinds-cdn\.com\/api\/v\d+\/m3u8s\/[a-zA-Z0-9]+\.m3u8'
anime = input("Enter the name:").lower().strip()
anime = anime.replace(" ","-")
response = requests.get(f"http://localhost:3000/watch/{anime}") #url for videos


print(response.content)
print("----"*20)
urls = []
match = re.findall(pattern=pattern, string=response.content.decode('utf-8'))
# print(match[0])


import subprocess
import os

def convert_m3u8_to_mp4(m3u8_url, output_filename):
    """
    Converts a video from a given M3U8 URL to an MP4 file using FFmpeg.
    """
    
    # Define the path to your ffmpeg executable if it's not in your system's PATH
    # If ffmpeg is in your PATH, you can just use 'ffmpeg'
    ffmpeg_path = 'ffmpeg' # or 'C:/path/to/ffmpeg/bin/ffmpeg.exe'

    # Construct the FFmpeg command as a list of arguments
    # Using a list is safer than a single string as it prevents shell injection vulnerabilities.
    command = [
        ffmpeg_path,
        '-i', m3u8_url,
        '-c', 'copy',
        output_filename
    ]

    print(f"Executing FFmpeg command:\n{' '.join(command)}")

    try:
        # Run the command
        # `capture_output=True` captures stdout and stderr
        # `text=True` decodes the output as text
        # `check=True` raises an exception if the command returns a non-zero exit code
        result = subprocess.run(command, check=True)

        print("\nFFmpeg output:")
        print(result.stdout)
        print("Video conversion successful!")

    except FileNotFoundError:
        print(f"Error: FFmpeg not found at '{ffmpeg_path}'.")
        print("Please ensure FFmpeg is installed and added to your system's PATH, or provide the full path to the executable.")
    except subprocess.CalledProcessError as e:
        print("\nAn error occurred during video conversion:")
        print(e.stderr)
        print("Process returned with code:", e.returncode)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Example Usage ---

# The M3U8 URL you want to download
m3u8_link = match[0]

# The name for the output video file
output_file = f"videos/{anime}.mp4"

# Call the function to start the conversion
convert_m3u8_to_mp4(m3u8_link, output_file)