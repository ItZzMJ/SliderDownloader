import json
import time
from pprint import pprint

from track import Track
from soundcloud import SoundCloud, BasicAlbumPlaylist, BasicTrack, MiniTrack
import re
import logging


class SoundcloudAPI:
    def __init__(self):
        logging.info("[SOUNDCLOUDAPI] Soundcloud init")
        self.client_id = self.get_client_id()
        self.sc = SoundCloud(self.client_id)

        #self.api = SoundcloudAPI()

    # get tracks from playlist
    def get_playlist_tracks(self, url):
        logging.info("[SOUNDCLOUDAPI] Getting Playlist Tracks")

        playlist = self.sc.resolve(url)

        tracks = playlist.tracks
        songs = []

        for track in tracks:
            if isinstance(track, MiniTrack):
                track = self.sc.get_track(track.id)

            title = track.title.replace("[", "").replace("]", "")\
                .replace("/", "").replace("<", "").replace(">", "").replace(":", "").replace("\\", "").replace("|", "")\
                .replace("?", "").replace("*", "")
            user = track.user.username.replace("[", "").replace("]", "").strip()\
                .replace("/", "").replace("<", "").replace(">", "").replace(":", "").replace("\\", "").replace("|", "")\
                .replace("?", "").replace("*", "")
            genre = track.genre
            artwork_url = track.artwork_url
            year = track.created_at.year

            # remove emojis
            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # emoticons
                                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                       u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                       "]+", flags=re.UNICODE)
            title = emoji_pattern.sub(r'', title)  # no emoji

            # remove 'Free Download' from title
            regex = re.compile(re.escape("free download"), re.IGNORECASE)
            title = regex.sub("", title)

            # remove 'freedownload' from title
            regex = re.compile(re.escape("freedownload"), re.IGNORECASE)
            title = regex.sub("", title)

            # remove 'Free dl' from title
            regex = re.compile(re.escape("free dl"), re.IGNORECASE)
            title = regex.sub("", title)

            # # remove 'out now' from title
            # regex = re.compile(re.escape("out now"), re.IGNORECASE)
            # title = regex.sub("", title)
            #
            # # remove 'now in' from title
            # regex = re.compile(re.escape("now in"), re.IGNORECASE)
            # title = regex.sub("", title)

            #if artist in title:
            #    title = title.replace(artist, "")
                #print(title)

            if " - " in title:
                splitted = title.split(" - ")
                artist = splitted[0]
                title = " - ".join(splitted[1:])
            else:
                artist = user

            title = title.replace("()", "").strip(" -|!,")

            purchase_url = track.purchase_url

            logging.info(f"[SOUNDCLOUDAPI] Found Track [name={title}, artists={artist}, genre={genre}, artwork_url={artwork_url}, year={year}]")

            songs.append(Track(name=title, artists=artist, genre=genre, artwork_url=artwork_url, year=year, purchase_url=purchase_url))

        return songs

    def get_playlist_name(self, url):
        logging.info(f"[SOUNDCLOUDAPI] Returning Playlistname")
        # get playlist
        playlist = self.sc.resolve(url)

        return playlist.title

    def get_client_id(self):
        with open("config.json", "r") as f:
            config = json.load(f)

        if config["soundcloud"]["client_id"]:
            return config["soundcloud"]["client_id"]
        else:
            print("Can't find the Soundcloud client_id. Check config.json file!")
            logging.error("[SOUNDCLOUDAPI] Can't find the Soundcloud client_id. Check config.json file!")
            return None


if __name__ == "__main__":
    x = SoundcloudAPI()
    tracks = x.get_playlist_tracks("https://soundcloud.com/mj-moebius/sets/download-1")
    print(tracks)
