import yt_dlp
import os
import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def get_video_info(video_url: str):
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', 'unknown')
        channel_name = info_dict.get('uploader', 'unknown')
        video_length = info_dict.get('duration_string', 'unknown')
        upload_date = info_dict.get('upload_date', 'unknown')
        formats = info_dict.get('formats', [])
        return video_title, channel_name, video_length, upload_date, formats

def get_channel_info(channel_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract channel info for videos
            info_dict_videos = ydl.extract_info(channel_url, download=False)

            # Extract channel name
            channel_name = info_dict_videos.get('channel', 'Channel name not found')

            return channel_name
        except Exception as e:
            return f"Error: {e}", 0, 0

def download_single_video(video_url: str, resolution: str):
    ydl_opts = {
        'verbose': True,
        'format': resolution,
        'merge_output_format': 'mp4',
        'cookiefile': "cookies.txt",
        'writeinfojson': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    print(f"Downloading video from: {video_url} with resolution: {resolution}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def download_channel_videos(channel_url, resolution: str):
    ydl_opts = {
        'verbose': True,
        'format': resolution,
        'merge_output_format': 'mp4',
        'cookiefile': "cookies.txt",
        'writeinfojson': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'download_archive': os.path.join(output_dir, 'downloaded_videos.txt')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)
        videos = info_dict.get('entries', [info_dict])

        for video in videos:
            video_title = video.get('title', 'unknown')
            print(f"Downloading video: {video_title}")
            ydl.download([video.get('webpage_url')])

def load_content():
    global info_label, resolution_frame
    for widget in resolution_frame.winfo_children():
        widget.destroy()
    info_label.config(text="")

    url = entry.get().strip()

    if 'watch?v=' in url:
        video_title, channel_name, video_length, upload_date, formats = get_video_info(url)
        info_label.config(text=f"Video Title: {video_title}\n"
                              f"Channel Name: {channel_name}\n"
                              f"Video Length: {video_length}\n"
                              f"Upload Date: {upload_date}")
        create_resolution_buttons(formats, url, 'video')
    elif '/channel/' in url or '/user/' in url:
        channel_name = get_channel_info(url)
        info_label.config(text=f"Channel Name: {channel_name}\n"
                                f"Warning! Downloading all videos from a channel may take a long time.")
        create_resolution_buttons([], url, 'channel')  # No individual resolutions for channels
    else:
        info_label.config(text="Invalid URL. Please enter a valid YouTube video or channel URL.")

def create_resolution_buttons(formats, url, content_type):
    global resolution_frame
    if content_type == 'video':
        button = ttk.Button(resolution_frame, text="Download Video", command=lambda: download_content(url, 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', content_type))
        button.pack(side=LEFT, padx=5)
    else:
        button = ttk.Button(resolution_frame, text="Download All", command=lambda: download_content(url, 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', content_type))
        button.pack(side=LEFT, padx=5)

def download_content(url, resolution, content_type):
    global output_dir
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_dir = f"downloads_{timestamp}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if content_type == 'video':
        download_single_video(url, resolution)
    elif content_type == 'channel':
        download_channel_videos(url, resolution)
    print("\nFinished downloads.\n")

def on_entry_key(event):
    if event.keysym == 'Return':
        load_content()

# Create the main window
root = ttk.Window(themename="superhero")
root.title("YouTube Downloader")
root.geometry("700x500")

# Create the input field
entry_label = ttk.Label(root, text="Enter YouTube Video or Channel URL:", font=('Calibri', 14))
entry_label.pack(pady=10)

entry_frame = ttk.Frame(root)
entry_frame.pack(pady=5)

entry = ttk.Entry(entry_frame, width=70, font=('Calibri', 12))
entry.pack(side=LEFT, padx=5)
entry.bind("<KeyRelease>", on_entry_key)

load_button = ttk.Button(entry_frame, text="Load", command=load_content, style='success.TButton')
load_button.pack(side=RIGHT, padx=5)

# Label for displaying information
info_label = ttk.Label(root, text="", font=('Calibri', 12), justify=LEFT)
info_label.pack(pady=10)

# Frame for resolution buttons
resolution_frame = ttk.Frame(root)
resolution_frame.pack(pady=10)

# Run the application
root.mainloop()
