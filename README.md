# YouTube Downloader

Python script utilizing yt-dlp to download either an entire channel's videos, or a single video from YouTube.

&nbsp;

## Prerequisites

- [Python](https://www.python.org/)

- yt-dlp

    - ```pip install yt-dlp```

- [ffmpeg](https://ffmpeg.org/)

    - Guide used to install ffmpeg and add to Windows PATH variables: https://phoenixnap.com/kb/ffmpeg-windows

&nbsp;

## IMPORTANT 

**You will need to add your YouTube account cookies to run this script properly.** Skipping this step will result in the script failing on age-restricted videos. However, if you're not downloading any age-restricted videos, it is not required.

Simplest way is to download the following plugin:

- Chrome: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc?hl=en
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/

Open a new window in incognito mode

Open a second tab, go to YouTube, and sign into a YouTube account <u>**_THAT IS NOT YOUR MAIN ACCOUNT_**</u>. Avoid using cookies from your main account to avoid potentially getting banned on it.

Close the YouTube tab and download all of your cookies to a text file titled `cookies.txt`

Paste this file in the root directory of this project.

&nbsp;

### Running the Script



In the root directory, run `download_vids.py`

```
python download_vids.py
```

Choose either "video" or "channel" to download

Paste link to the video or YouTube channel.

The script will automatically download the videos in mp4 to a folder titled with the channel name and current time.