from pprint import pprint
from track import Track
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os


class SpotifyAPI:
    def __init__(self):
        load_dotenv(".env")
        self.credentials = self.get_credentials()
        self.spotify = spotipy.Spotify(client_credentials_manager=self.credentials)

    # login
    def get_credentials(self):
        return SpotifyClientCredentials(
            client_id=os.getenv("SP_CLIENT_ID"),
            client_secret=os.getenv("SP_SECRET"))

    # get name of playlist
    def get_playlist_name(self, url):
        return self.spotify.playlist(url, fields='name')['name']

    # get artwork url
    def get_img_url(self, song):
        try:
            img_url = song['track']['album']['images'][0]['url']
        except Exception:
            img_url = None
        return img_url

    # get first genre of first artist
    def get_genre(self, song):
        try:
            # get artist ID
            urn = song['track']['artists'][0]['uri']

            # get artist
            artist = self.spotify.artist(urn)

            # get genre
            genre = artist["genres"][0]

        except Exception:
            genre = None

        return genre

    # get tracks from playlist
    def get_playlist_tracks(self, url):
        tracks = []
        result = self.spotify.playlist(url, fields='name,next,tracks')['tracks']
        songs = result['items']

        # if more than 100 songs in playlist
        while result['next']:
            result = self.spotify.next(result)
            songs.extend(result['items'])

        # get usefull info
        for song in songs:
            name = song['track']['name']

            # get artwork
            img_url = self.get_img_url(song)

            # get genre
            genre = self.get_genre(song)

            artists = []
            for artist in song['track']['artists']:
                artists.append(artist['name'])

            tracks.append(Track(name=name, artists=artists, genre=genre, artwork_url=img_url))

        return tracks

# TODO: remove
# playlist = "https://open.spotify.com/playlist/1B0gmbwIiJBkpFslXZBsZw?si=7c2fc17f99294cc8"
# api = SpotifyAPI()
# y = api.get_playlist_tracks(url=playlist)
#
# for track in y:
#     print(f"{track.name} - {track.print_artists()} | {track.genre} | {track.artwork_url}")
#tracks = y["tracks"]
#pprint(y)

