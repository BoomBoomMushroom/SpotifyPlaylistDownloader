import eyed3

def add_metadata(filepath, artist, title, albumName):
    """Adds artist and title metadata to an MP3 file.

    Args:
        filepath (str): The path to the MP3 file.
        artist (str): The name of the artist.
        title (str): The title of the song.
    """
    try:
        audiofile = eyed3.load(filepath)
        if audiofile.tag is None:
            audiofile.initTag()
        audiofile.tag.artist = artist
        audiofile.tag.title = title
        audiofile.tag.album = albumName
        audiofile.tag.save()
        print(f"Metadata added to {filepath}: Artist - {artist}, Title - {title}, Album - {albumName}")
    except Exception as e:
         print(f"An error occurred: {e}")

# For multiple artists do "ARTIST 1; ARTIST 2; ARTIST 3"
if __name__ == "__main__":
    file_path = "E:\\Liked Songs 3_27_2025\\6 Weeks_Beach Bunny.mp3"
    artist_name = "Beach Bunny; Oliva Rodrigo"
    song_title = "6 Weeks"
    add_metadata(file_path, artist_name, song_title, "Emotional Creature")