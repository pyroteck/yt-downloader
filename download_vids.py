import yt_dlp
import os
import datetime

def download_single_video(video_url: str):
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        channel_name = info_dict.get('uploader', 'unknown')  # Use 'uploader' instead of 'channel'
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')
        output_dir = f"{channel_name}_single_video_{timestamp}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        ydl_opts = {
            'verbose': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'merge_output_format': 'mp4',
            'cookiefile': "cookies.txt",
            'writeinfojson': True,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        }

        print(f"Downloading video from: {video_url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

def download_channel_videos(channel_url):
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(channel_url, download=False)
        channel_name = info_dict.get('channel', 'unknown')
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"{channel_name}_channel_{timestamp}"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        ydl_opts = {
            'verbose': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'merge_output_format': 'mp4',
            'cookiefile': "cookies.txt",
            'writeinfojson': True,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'download_archive': os.path.join(output_dir, 'downloaded_videos.txt')
        }

        videos = info_dict.get('entries', [info_dict])

        for video in videos:
            video_title = video.get('title', 'unknown')
            print(f"Downloading video: {video_title}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video.get('webpage_url')])

def main():
    while True:
        choice = input("Do you want to download a single video or a channel? (Type 'video' or 'channel'): ").strip().lower()

        if choice == 'video':
            video_url = input("Enter the URL of the video: ").strip()
            download_single_video(video_url)
            break
        elif choice == 'channel':
            channel_url = input("Enter the URL of the channel: ").strip()
            download_channel_videos(channel_url)
            break
        else:
            print("Invalid choice. Please type 'video' or 'channel'.")

    print("\nFinished downloads.\n")

if __name__ == '__main__':
    main()
