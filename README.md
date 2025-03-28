# Spotify Playlist Downloader

Are you trying to find a good way to download your Spotify playlists? Well, look a little bit farther because this solution takes a little bit of work.

# Getting Started

1. Install the required pip packages: Pytube, version 12.1.0, and Pytubefix, version 8.12.2. I am also using Python 3.11.3 and Pip 25.0.1
2. Next make a secrets.json and put this in:

```
{
    "ClientID": "YOUR_CLIENT_ID_HERE",
    "ClientSecret": "YOUR_CLIENT_SECRET_HERE"
}
```

3. Make a Spotify application at https://developer.spotify.com/dashboard, and then put in your client id and client secret.
4. (Optional) Go to around line 117 of main.py. Something like "youtubeSearchAndDownload.searchForVideos" The 'Official Audio' part is what we _can_ change if we'd like. I'd stick with something like 'Official Audio', 'Official Lyrics', or 'Lyric Video' as that tends to eliminate the music videos which I'd like to remove due to the extra bloat. but feel free to leave it as just "{searchTerm}"
5. Now run main.py and choose where to have the m4as downloaded (or mp3s), if you leave it blank it will default to the songs folder in the directory of main.py
6. Now say "y" or "n" to if you want to automatically convert the m4as (default file type b/c of Pytube) to mp3s. You need ffmpeg for this to work
7. Then choose either 1 or 2. 1 is for a playlist that is publicly accessible. 2 is for copy and pasting from spotify into it, which is useful for your liked songs. It's also good for adding singular songs
8. Then enter/paste the playlist url or the song URLs depending on which you choose
9. Now Python will go search and download everything. If it has trouble with some try just doing that one song by itself
10. Note: If you run the program when there are already the same songs in the folder, then it will never rename itself and it will be stuck as a weird file that you need to rename yourself.

# How Does It Work?

I use Spotify's API to get the all the songs' titles, artists, and length. Then I use Pytube to search YouTube to search for the audios. Once I find a close match (by getting the video who's length is closest to Spotify's length). Pytube then downloads the audio for that video and puts in the output folder, also renaming it in the process. Then we use FFMpeg to convert the default downloads, m4as, into mp3s. Then use Spotify's data to assign mp3 metadata like artists, song title, and album name!

If you have any issue make a PR or an issue. You can do whatever you want with this code! <3
