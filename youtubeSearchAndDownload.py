import pytubefix as pytube
import os

def timeToSeconds(time_str):
    parts = list(map(int, time_str.split(":")))
    return sum(x * 60 ** i for i, x in enumerate(reversed(parts)))

def searchForVideos(searchText):
    searchResultVideos = []
    s = pytube.Search(searchText)
    
    searchContentsRaw = s.fetch_query()["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
    searchContents = None
    for raw in searchContentsRaw:
        if "itemSectionRenderer" in raw:
            searchContents = raw["itemSectionRenderer"]["contents"]
            break

    for content in searchContents:
        # Check if a video (not a short)
        if "videoRenderer" not in content: continue
        realContent = content["videoRenderer"]
        
        videoLength = realContent["lengthText"]["simpleText"] # in HH:MM:SS
        videoURL = "https://youtube.com" + realContent["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"]
        #print(videoLength, videoURL)
        videoLengthSeconds = timeToSeconds(videoLength)
        
        searchResultVideos.append({"LengthString": videoLength, "Length": videoLengthSeconds, "URL": videoURL})
    
    return searchResultVideos

def downloadVideo(videoURL, outputDir="./songs", fileName=""):
    yt = pytube.YouTube(videoURL)
    videoStreams = yt.streams.filter(only_audio=True)
    video = None
    for stream in videoStreams:
        if video == None:
            video = stream
            continue
        if stream.itag > video.itag:
            video = stream
    
    out_file = video.download(outputDir, fileName)
    
    """
    # For some reason the downloaded file has to extention (causing songs like "Ms. California" and "Mr. Brightside" to be saved as "Ms.m4a" and "Mr.m4a" respectively)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.m4a'
    """
    
    os.rename(out_file, out_file + ".m4a")
    return True
