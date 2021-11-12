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
            #for att in dir(song):
            #    print(att, getattr(song, att))
            #exit(0)
            artist = [song.artist]
            genre = song.genre
            name = song.title
            img_url = song.artwork_url
            year = song.created_at.split("-")[0]
            songs.append(Track(name=name, artists=artist, genre=genre, artwork_url=img_url, year=year))

        return songs

    # get name of the playlist
    def get_playlist_name(self, url):
        # get playlist
        playlist = self.api.resolve(url)

        return playlist.title

        # for attr in dir(playlist): dump vars
        #     print("obj.%s = %r" % (attr, getattr(playlist, attr)))
        # exit()



# TODO: remove
x = Soundcloud()
url = "https://soundcloud.com/mj-moebius/sets/tech-house"
tracks = x.get_playlist_tracks(url)
#
# for track in tracks:
#     print(f"{track.name} - {track.print_artists()} | {track.genre} | {track.artwork_url}")

