from track import Track
from soundcloud import SoundCloud, BasicAlbumPlaylist, BasicTrack, MiniTrack
import re
import logging


class SoundcloudAPI:
    def __init__(self):
        logging.info("[SOUNDCLOUDAPI] Soundcloud init")
        self.client_id = "BcelrHPTZdE9G60fL6hI8bl4rBIFHPED"
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

            title = track.title.replace("[", "").replace("]", "")
            user = track.user.username.replace("[", "").replace("]", "").strip()
            genre = track.genre
            artwork_url = track.artwork_url
            year = track.created_at.year

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

            logging.info(f"[SOUNDCLOUDAPI] Found Track [name={title}, artists={artist}, genre={genre}, artwork_url={artwork_url}, year={year}]")

            songs.append(Track(name=title, artists=artist, genre=genre, artwork_url=artwork_url, year=year))

        return songs

    def get_playlist_name(self, url):
        logging.info(f"[SOUNDCLOUDAPI] Returning Playlistname")
        # get playlist
        playlist = self.sc.resolve(url)

        return playlist.title




#
# x = SoundcloudAPI()
# url = "https://soundcloud.com/heatedbread/sets/bass-house-1"
# tracks = x.get_playlist_tracks(url)
#
# for track in tracks:
#     print(f"{track.name} - {track.print_artists()} | {track.genre} | {track.artwork_url}")

