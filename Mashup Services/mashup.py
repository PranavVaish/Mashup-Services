import os
import glob
from yt_dlp import YoutubeDL
from moviepy.editor import AudioFileClip, concatenate_audioclips

try:
    # Try v2.0 import
    from moviepy import AudioFileClip, concatenate_audioclips
except ImportError:
    # Fallback to v1.0 import
    from moviepy.editor import AudioFileClip, concatenate_audioclips
def cleanup_temp():
    """Safely cleans up the temp_audio directory."""
    if os.path.exists("temp_audio"):
        # 1. Remove all files inside the directory
        files = glob.glob("temp_audio/*")
        for f in files:
            try:
                os.remove(f)
            except Exception:
                pass
        
        # 2. Remove the empty directory
        try:
            os.rmdir("temp_audio")
        except Exception:
            pass

def create_mashup(singer, n, duration, output_filename):
    """
    Downloads videos and creates a mashup.
    Returns True if successful, False otherwise.
    """
    # Clean up any leftovers from previous runs
    cleanup_temp() 
    
    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")

    print(f"Server: Searching for {singer}...")
    
    # --- PHASE 1: SEARCH ---
    ydl_opts_search = {
        'format': 'bestaudio/best',
        'quiet': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'extract_flat': True, # Fast search (don't download yet)
        'noplaylist': True,
    }

    valid_urls = []
    try:
        with YoutubeDL(ydl_opts_search) as ydl:
            # Search for 2x the requested amount to filter out long videos
            search_query = f"ytsearch{n*2}:{singer} song"
            result = ydl.extract_info(search_query, download=False)
            
            if 'entries' in result:
                for entry in result['entries']:
                    if not entry: continue
                    # Filter: Only accept videos shorter than 10 mins (600s)
                    vid_duration = entry.get('duration')
                    if vid_duration and vid_duration < 600:
                        valid_urls.append(entry['url'])
                        if len(valid_urls) >= n:
                            break
    except Exception as e:
        print(f"Search Error: {e}")
        return False

    if not valid_urls:
        print("No valid videos found.")
        return False

    print(f"Server: Downloading {len(valid_urls)} videos...")

    # --- PHASE 2: DOWNLOAD ---
    ydl_opts_download = {
        'format': 'bestaudio/best',
        'outtmpl': "temp_audio/%(title)s.%(ext)s",
        'quiet': True,
        'ignoreerrors': True,
        'no_warnings': True,
        # Use Android client to bypass 'Sign in' errors
        'extractor_args': {'youtube': {'player_client': ['android']}},
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    # Use cookies.txt if it exists (highly recommended)
    if os.path.exists("cookies.txt"):
        print("Using cookies.txt for authentication")
        ydl_opts_download['cookiefile'] = "cookies.txt"

    try:
        with YoutubeDL(ydl_opts_download) as ydl:
            ydl.download(valid_urls)
    except Exception as e:
        print(f"Download Error: {e}")
        # Continue anyway, in case some files downloaded successfully

    # --- PHASE 3: MERGE ---
    audio_files = glob.glob("temp_audio/*.mp3")
    if not audio_files:
        print("No audio files were downloaded.")
        return False

    print(f"Server: Merging {len(audio_files)} clips...")
    clips = []
    
    try:
        for file in audio_files:
            try:
                clip = AudioFileClip(file)
                # Cut the clip to the requested duration
                # Use 'min' to handle clips shorter than the requested duration
                subclip = clip.subclip(0, min(duration, clip.duration))
                clips.append(subclip)
            except Exception as e:
                print(f"Skipping corrupt file {file}: {e}")

        if clips:
            final_clip = concatenate_audioclips(clips)
            final_clip.write_audiofile(output_filename)
            
            # Close all clips to release file locks (Important for Windows)
            final_clip.close()
            for c in clips: 
                c.close()
            
            # Cleanup temp files after success
            cleanup_temp()
            return True
        else:
            return False

    except Exception as e:
        print(f"Processing Error: {e}")
        return False