import sys
import os
import time
import glob
import traceback
from yt_dlp import YoutubeDL
try:
    from moviepy.editor import AudioFileClip, concatenate_audioclips
except ImportError:
    try:
        from moviepy import AudioFileClip, concatenate_audioclips
    except ImportError:
        print("Error: moviepy not installed.")
        sys.exit(1)

import imageio_ffmpeg

def download_audio(singer, n):
    """Downloads n audio files using cookies.txt if available."""
    query = f"{singer} audio"
    output_template = "temp_audio/%(title)s.%(ext)s"
    
    # Check for cookies.txt in the current directory
    if os.path.exists("cookies.txt"):
        print("DEBUG: Found cookies.txt! Using it for authentication.")
        cookie_arg = "cookies.txt"
    else:
        print("WARNING: cookies.txt not found. YouTube might block this request.")
        print("If it fails, install 'Get cookies.txt LOCALLY' extension and save file here.")
        cookie_arg = None

    # Common options for both Search and Download
    common_opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        # 'client': 'android' mimics a mobile phone, often bypassing bot checks
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
    }
    
    if cookie_arg:
        common_opts['cookiefile'] = cookie_arg

    # Phase 1: Search
    print(f"Searching for videos of {singer}...")
    valid_urls = []
    
    search_opts = common_opts.copy()
    search_opts.update({
        'extract_flat': True, # Don't download, just get metadata
        'playlist_items': f"1-{n*3}", # Fetch more to filter later
    })

    with YoutubeDL(search_opts) as ydl:
        try:
            # ytsearchN:query
            result = ydl.extract_info(f"ytsearch{n*3}:{query}", download=False)
            if 'entries' in result:
                for entry in result['entries']:
                    if not entry: continue
                    # Filter for length (e.g., < 10 mins)
                    if entry.get('duration') and entry.get('duration') < 600:
                        valid_urls.append(entry['url'])
                        print(f"DEBUG: Found {entry.get('title')}")
                        if len(valid_urls) >= n:
                            break
        except Exception as e:
            print(f"Search Error: {e}")

    if not valid_urls:
        print("No valid videos found.")
        return

    print(f"Downloading {len(valid_urls)} videos...")

    # Phase 2: Download
    dl_opts = common_opts.copy()
    dl_opts.update({
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })

    with YoutubeDL(dl_opts) as ydl:
        ydl.download(valid_urls)

def process_audio(duration, output_file):
    """Merges the downloaded audio files."""
    audio_files = glob.glob("temp_audio/*.mp3")
    
    if not audio_files:
        return False

    print(f"Processing {len(audio_files)} files...")
    clips = []
    for file in audio_files:
        try:
            clip = AudioFileClip(file)
            # Clip the audio to the specified duration
            subclip = clip.subclip(0, min(duration, clip.duration))
            clips.append(subclip)
        except Exception as e:
            print(f"Skipping {file}: {e}")

    if clips:
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(output_file)
        # Cleanup clips to release file handles
        final_clip.close()
        for c in clips: c.close()
        return True
    return False

def cleanup():
    """Deletes temporary folder."""
    if os.path.exists("temp_audio"):
        for f in glob.glob("temp_audio/*"):
            os.remove(f)
        os.rmdir("temp_audio")

def main():
    if len(sys.argv) != 5:
        print("Usage: python 102303194.py <Singer> <Count> <Duration> <Output>")
        sys.exit(1)

    singer = sys.argv[1]
    n = int(sys.argv[2])
    duration = int(sys.argv[3])
    output = sys.argv[4]

    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")

    try:
        download_audio(singer, n)
        if process_audio(duration, output):
            print(f"Success! Saved to {output}")
        else:
            print("Failed to create mashup.")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
    finally:
        cleanup()

if __name__ == "__main__":
    main()