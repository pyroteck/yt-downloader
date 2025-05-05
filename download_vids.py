import yt_dlp
import os
import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import concurrent.futures
import threading
import re
from tkinter import filedialog
import signal
import sys

# Add a flag to indicate if the program should terminate
terminate_flag = threading.Event()

def signal_handler(sig, frame):
    print("SIGINT received, terminating...")
    terminate_flag.set()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_video_info(video_url: str):
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', 'unknown')
        channel_name = info_dict.get('uploader', 'unknown')
        video_length = info_dict.get('duration_string', 'unknown')
        upload_date = info_dict.get('upload_date', 'unknown')
        formats = info_dict.get('formats', [])

        upload_date = datetime.datetime.strptime(upload_date, '%Y%m%d').strftime('%B %d, %Y')
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

def download_single_video(video_url: str, resolution: str, progress_callback):
    ydl_opts = {
        'verbose': True,
        'format': resolution,
        'merge_output_format': 'mp4',
        'cookiefile': cookies_file,
        'writeinfojson': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_callback],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def download_channel_videos(channel_url, resolution: str, progress_callback):
    ydl_opts = {
        'verbose': True,
        'format': resolution,
        'merge_output_format': 'mp4',
        'cookiefile': cookies_file,
        'writeinfojson': True,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'download_archive': os.path.join(output_dir, 'downloaded_videos.txt'),
        'progress_hooks': [progress_callback],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)
        videos = info_dict.get('entries', [info_dict])

        for video in videos:
            if terminate_flag.is_set():
                print("Terminating download due to SIGINT.")
                return
            video_title = video.get('title', 'unknown')
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
                              f"Upload Date: {upload_date}",
                              bootstyle='default')
        create_resolution_buttons(formats, url, 'video')
    elif '/channel/' in url or '/user/' in url:
        channel_name = get_channel_info(url)
        info_label.config(text=f"Channel Name: {channel_name}\n"
                              f"Warning! Downloading all videos from a channel may take a long time.",
                              bootstyle='default')
        create_resolution_buttons([], url, 'channel')
    else:
        info_label.config(text="Invalid URL. Please enter a valid YouTube video or channel URL.", bootstyle="warning")

def remove_ansi_escape_sequences(text):
    return re.sub("[^0-9^.]", "", re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', text))

def update_progress_bar(d):
    if d['status'] == 'downloading':
        percent = re.sub("[^0-9^.]", "", re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', d.get('_percent_str', '0.0%').strip('%').strip()))
        try:
            progress_var.set(float(percent))
        except ValueError:
            print(f"Failed to convert percent to float: {percent}")
        root.update_idletasks()

def download_content(url, resolution, content_type):
    global output_dir, progress_var, progress_bar, cookies_file, entry, load_button, download_dir_button, cookies_file_button, download_dir_entry, cookies_file_entry

    # Disable all buttons and entry boxes
    entry.config(state=DISABLED)
    load_button.config(state=DISABLED)
    download_dir_button.config(state=DISABLED)
    cookies_file_button.config(state=DISABLED)
    download_dir_entry.config(state=DISABLED)
    cookies_file_entry.config(state=DISABLED)

    if not output_dir:
        output_dir = os.getcwd()  # Default to current working directory if no directory is set

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
    output_dir = os.path.join(output_dir, f"downloads_{timestamp}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    progress_var = ttk.DoubleVar()
    progress_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=300, mode='determinate', variable=progress_var)
    progress_bar.pack(pady=10)

    def download_task():
        try:
            if content_type == 'video':
                download_single_video(url, resolution, update_progress_bar)
            elif content_type == 'channel':
                download_channel_videos(url, resolution, update_progress_bar)
        finally:
            # Re-enable all buttons and entry boxes
            entry.config(state=NORMAL)
            load_button.config(state=NORMAL)
            download_dir_button.config(state=NORMAL)
            cookies_file_button.config(state=NORMAL)
            download_dir_entry.config(state=NORMAL)
            cookies_file_entry.config(state=NORMAL)
            progress_bar.destroy()

    thread = threading.Thread(target=download_task)
    thread.daemon = True  # Set the thread as a daemon
    thread.start()

# Modify the create_resolution_buttons function to use the new state management
def create_resolution_buttons(formats, url, content_type):
    global resolution_frame
    if content_type == 'video':
        button = ttk.Button(resolution_frame, text="Download Video", command=lambda: download_content(url, 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', content_type))
        button.pack(side=LEFT, padx=5)
    else:  # content_type == 'channel'
        button = ttk.Button(resolution_frame, text="Download All", command=lambda: download_content(url, 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', content_type))
        button.pack(side=LEFT, padx=5)

def on_entry_key(event):
    if event.keysym == 'Return':
        load_content()

def select_download_directory():
    global output_dir
    output_dir = filedialog.askdirectory(initialdir=os.getcwd(), title="Select Download Directory")
    if output_dir:
        download_dir_entry.delete(0, END)
        download_dir_entry.insert(0, output_dir)

def select_cookies_file():
    global cookies_file
    cookies_file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select Cookies File", filetypes=[("Text files", "*.txt")])
    if cookies_file:
        cookies_file_entry.delete(0, END)
        cookies_file_entry.insert(0, cookies_file)

def on_close():
    print("Window closed, terminating...")
    terminate_flag.set()
    sys.exit(0)

# Initialize global variables
output_dir = os.getcwd()  # Default to current working directory
cookies_file = os.path.join(os.getcwd(), "cookies.txt")  # Default to cookies.txt in the current working directory

# Create the main window
root = ttk.Window(themename="superhero")
root.title("YouTube Downloader")
root.geometry("700x500")

# Set the custom close handler
root.protocol("WM_DELETE_WINDOW", on_close)

# Create the input field
entry_label = ttk.Label(root, text="Enter YouTube Video or Channel URL:", font=('Calibri', 18, "bold"))
entry_label.pack(pady=10)

entry_frame = ttk.Frame(root)
entry_frame.pack(pady=5)

entry = ttk.Entry(entry_frame, width=70, font=('Calibri', 12))
entry.pack(side=LEFT, padx=5)
entry.bind("<KeyRelease>", on_entry_key)

load_button = ttk.Button(entry_frame, text="Load", command=load_content, style='success.TButton', width=8)
load_button.pack(side=RIGHT, padx=5)

# Create the input field for download directory
download_label = ttk.Label(root, text="Choose download directory:", font=('Calibri', 14, "bold"))
download_label.pack(pady=3)

# Frame for download directory entry and button
download_dir_frame = ttk.Frame(root)
download_dir_frame.pack(pady=3)

# Entry box for download directory
download_dir_entry = ttk.Entry(download_dir_frame, width=70, font=('Calibri', 12))
download_dir_entry.insert(0, output_dir)  # Set default value
download_dir_entry.pack(side=LEFT, padx=5)

# File selector for download directory
download_dir_button = ttk.Button(download_dir_frame, text="Browse", command=select_download_directory, style='info.TButton', width=8)
download_dir_button.pack(side=RIGHT, padx=5)

# Create the input field for cookies file
cookies_label = ttk.Label(root, text="Choose cookies file:", font=('Calibri', 14, "bold"))
cookies_label.pack(pady=3)

# Frame for cookies file entry and button
cookies_file_frame = ttk.Frame(root)
cookies_file_frame.pack(pady=3)

# Entry box for cookies file
cookies_file_entry = ttk.Entry(cookies_file_frame, width=70, font=('Calibri', 12))
cookies_file_entry.insert(0, cookies_file)  # Set default value
cookies_file_entry.pack(side=LEFT, padx=5)

# File selector for cookies file
cookies_file_button = ttk.Button(cookies_file_frame, text="Browse", command=select_cookies_file, style='info.TButton', width=8)
cookies_file_button.pack(side=RIGHT, padx=5)

# Label for displaying information
info_label = ttk.Label(root, text="", font=('Calibri', 12), justify=LEFT)
info_label.pack(pady=10)

# Frame for resolution buttons
resolution_frame = ttk.Frame(root)
resolution_frame.pack(pady=10)

# Run the application
root.mainloop()
