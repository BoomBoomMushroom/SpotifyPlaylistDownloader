import requests
import json
import concurrent.futures
import time

with open("secrets.json", "r") as secretsFile:
    secrets = json.load(secretsFile)

outputDir = input("Where do we save the songs to? (default is just /songs of this file)\n")
if outputDir == "": outputDir = "./songs"

doPlaylistURL = False
while True:
    inputForInputType = input("Do you want to input a (1) public playlist URL or (2) copy and paste the songs (copy & paste is very quick and works for liked songs)\n")
    if inputForInputType != "1" and inputForInputType != "2": continue
    
    doPlaylistURL = inputForInputType=="1"
    break

songLinks = []
if doPlaylistURL == False:
    # Get the song links
    while True:
        userPasteInput = input("""
    Use CTRL + A to select all the songs and then CTRL + C to copy them to clipboard. Then paste it here
    If you've already pasted then just hit enter until this message goes away (either in 1 or 2 presses)\n""")
        
        if userPasteInput == "": break
        
        songLinks.append(userPasteInput)

    #print(songLinks)

playlistURL = ""
if doPlaylistURL:
    playlistURL = input("Enter your playlist URL: ")

def getAccessToken():
    tokenRequest = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Content-Type":"application/x-www-form-urlencoded"},
        data={"grant_type": "client_credentials", "client_id": secrets["ClientID"], "client_secret": secrets["ClientSecret"]}
    )
    
    tokenResponse = tokenRequest.json()
    """
    {
        'access_token': '',
        'token_type': 'Bearer',
        'expires_in': 3600
    }
    """
    
    return f"{tokenResponse['token_type']} {tokenResponse['access_token']}" # Ex. Bearer XXXX (format will be used later in auth header)

def getSongsInPlaylist(accessToken, playlistURL):
    playlistID = playlistURL.split("spotify.com/playlist/")[1].split("?")[0]
    songsInPlaylistRequest = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlistID}/tracks",
        headers={"Authorization": accessToken}
    )
    
    # https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks
    # Response Format ^^^^
    return songsInPlaylistRequest.json()

def getSongsData(accessToken, songURLList):
    songIDs = []
    for songURL in songURLList:
        songID = songURL.split("spotify.com/track/")[1].split("?")[0]
        songIDs.append(songID)
    
    songIdsString = ",".join(songIDs)
    songsDataRequest = requests.get(f"https://api.spotify.com/v1/tracks?ids={songIdsString}", headers={"Authorization": accessToken})
    songsDataJsonOut = songsDataRequest.json()
    return songsDataJsonOut
    
accessToken = getAccessToken()


songsInPlaylist = []

if doPlaylistURL:
    items = getSongsInPlaylist(accessToken, playlistURL)["items"]
    for item in items:
        songsInPlaylist.append(item["track"])
else:
    songsInPlaylist = getSongsData(accessToken, songLinks)["tracks"]

songFileNames = []
songSearchTerms = []
songLengths = []
for song in songsInPlaylist:
    songName = song["name"]
    songArtist = song["artists"][0]["name"]
    songLength = song["duration_ms"] / 1000 # in seconds
    
    songFileNames.append(f"{songName}_{songArtist}")
    songSearchTerms.append(f"{songName} by {songArtist}")
    songLengths.append(songLength)

#print(songSearchTerms)

# Look up "songSearchTerm Official Audio/Lyrics" and get the top results
# then check the length of each of those videos and which ever one's length is closest to the spotify's song length wins and we download it

import youtubeSearchAndDownload

notComplete = []
for searchTerm in songSearchTerms: notComplete.append(searchTerm)

def threadDownload(i):
    global notComplete
    searchTerm = songSearchTerms[i]
    songLength = songLengths[i]
    
    results = youtubeSearchAndDownload.searchForVideos(f"{searchTerm} Offical Audio")
    bestResultURL = None
    bestTimeDiff = None
    for result in results:
        timeDiff = abs(songLength - result["Length"])
        if timeDiff <= 1.5: timeDiff = 0 # We can excuse +/- 1.5 seconds
        
        if bestResultURL == None or timeDiff < bestTimeDiff:
            bestResultURL = result["URL"]
            bestTimeDiff = timeDiff
    
    #print(bestResultURL, searchTerm, songLength)
    print(f"Download Starting for {songFileNames[i]}")
    didSucceed = youtubeSearchAndDownload.downloadVideo(bestResultURL, outputDir=outputDir, fileName=songFileNames[i])
    if didSucceed:
        print(f"Successfully downloaded {songFileNames[i]}")
        notComplete.remove(searchTerm)
        pass
    else:
        #print(f"Failed to download {songFileNames[i]}")
        pass
    
    #break


with concurrent.futures.ThreadPoolExecutor(max_workers=len(songSearchTerms)) as executor:
    executor.map(threadDownload, range(0, len(songSearchTerms)))

while True:
    if len(notComplete) == 0: break
    time.sleep(1)
    print(", ".join(notComplete))

print("Done downloading playlist!")