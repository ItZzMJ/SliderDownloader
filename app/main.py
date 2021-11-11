from spotifyAPI import SpotifyAPI
from soundcloudAPI import Soundcloud
from downloader import Downloader
import pathlib
import os
from time import sleep


class Main:
    def __init__(self):
        self.url = "https://soundcloud.com/mj-moebius/sets/test"

    def main(self):
        # start gui

        # set configs through gui
        output_dir = os.path.join(pathlib.Path().resolve(), "music")

        # get Tracks
        try:
            tracks = self.get_tracks(self.url)
        except Exception as e:
            print(e)
            exit(-1)

        else:
            # download Tracks
            downloader = Downloader(output_dir, True)
            try:
                downloader.download(tracks)
            finally:
                downloader.tear_down()

    def get_tracks(self, url):
        # determine if soundcloud or spotify
        if "soundcloud" in url:
            soundcloud = Soundcloud()

            # get Tracks
            return soundcloud.get_playlist_tracks(url)

        elif "spotify" in url:
            spotify = SpotifyAPI()

            # get Tracks
            return spotify.get_playlist_tracks(url)

        else:
            raise Exception("Soundcloud oder Spotify URL plsss")


if __name__ == "__main__":
    main = Main()
    main.main()
    print("Finished!")


