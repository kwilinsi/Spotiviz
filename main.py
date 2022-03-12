from src.cleaner import spotifyDownload


def main():
    # gui.startGui()

    path = 'B:\\Spotify\\data\\simon\\simon-1jul20'

    spotifyDownload.SpotifyDownload(path)


# Start the program
main()
