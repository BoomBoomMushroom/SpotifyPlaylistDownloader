import requests
import json
import concurrent.futures
import time
import os

with open("secrets.json", "r") as secretsFile:
    secrets = json.load(secretsFile)

outputDir = input("Where do we save the songs to? (default is just /songs of this file)\n")
if outputDir == "": outputDir = "./songs"

doConvertToMP3 = input("Do you want to automatically convert the files into MP3s instead of M4As? (requires FFMpeg to be installed) y/n\n").lower() == "y"

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

def listToEnglish(names):
    if not names:
        return ""
    elif len(names) == 1:
        return names[0]
    elif len(names) == 2:
        return f"{names[0]} and {names[1]}"
    else:
        return f"{', '.join(names[:-1])}, and {names[-1]}"

def removeNonFileCharacters(string: str):
    notAllowed = ["\\", "/", ":", "*", "?", "\"", "<", ">", "|"]
    return ''.join(c for c in string if c not in notAllowed)

songFileNameToMP3Data = {}

songFileNames = []
songSearchTerms = []
songLengths = []
for song in songsInPlaylist:
    songName = song["name"]
    songArtistNameList = []
    for artist in song["artists"]:
        songArtistNameList.append(artist["name"])
    artistToPutInFileName = songArtistNameList[0]
    albumName = song["album"]["name"]
    
    songArtists = listToEnglish(songArtistNameList)
    songLength = song["duration_ms"] / 1000 # in seconds
    
    # Remove all non windows file name allowed characters
    # We use the filename to get a key later, and it can be different if we use disallowed characters
    songFileName = f"{songName}_{artistToPutInFileName}"
    songFileName = removeNonFileCharacters(songFileName)
    
    songFileNames.append(songFileName)
    songSearchTerms.append(f"{songName} by {artistToPutInFileName}")
    songLengths.append(songLength)
    
    songFileNameToMP3Data[songFileName] = {
        "Artists": songArtists,
        "SongName": songName,
        "AlbumName": albumName
    }
    
    print(f"Meta key made: {songFileName}")


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
        if timeDiff <= 1.5: timeDiff = 0 # We can excuse ± 1.5 seconds
        
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

import m4a_to_mp3
import MP3MetadataAdder

if doConvertToMP3:
    print("Now converting playlist...")
    m4a_to_mp3.convert_all_m4a(outputDir, outputDir)
    m4a_to_mp3.deleteAllM4As(outputDir)
    print("Done converting! Now adding metadata")
    
    for filename in os.listdir(outputDir):
        if filename.endswith("mp3") == False: continue
        filePath = os.path.join(outputDir, filename)
        
        metaKey = filename.split(".mp3")[0]
        
        #print(songFileNameToMP3Data.keys())
        print(f"Trying to add metadata using key {metaKey}")
        MP3MetadataAdder.add_metadata(
            filePath,
            songFileNameToMP3Data[metaKey]["Artists"],
            songFileNameToMP3Data[metaKey]["SongName"],
            songFileNameToMP3Data[metaKey]["AlbumName"],
        )
        print("Done adding metadata")
        
print("Finished everything!")

