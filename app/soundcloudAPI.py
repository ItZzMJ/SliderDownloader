from pprint import pprint
from track import Track
from sclib import SoundcloudAPI, Playlist


class Soundcloud:
    def __init__(self):
        self.api = SoundcloudAPI()

    # get tracks from playlist
    def get_playlist_tracks(self, url):
        songs = []
        # get playlist
        playlist = self.api.resolve(url)
        assert type(playlist) is Playlist

        # iterate through playlist and write infos in tracks
        for song in playlist.tracks:
            artist = [song.artist]
            genre = song.genre
            name = song.title
            img_url = song.artwork_url
            songs.append(Track(name=name, artists=artist, genre=genre, artwork_url=img_url))

        return songs


# TODO: remove
# x = Soundcloud()
# url = "https://soundcloud.com/mj-moebius/sets/tech-house"
# tracks = x.get_playlist(url)
#
# for track in tracks:
#     print(f"{track.name} - {track.print_artists()} | {track.genre} | {track.artwork_url}")

