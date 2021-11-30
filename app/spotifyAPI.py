from track import Track
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging


class SpotifyAPI:
    def __init__(self):
        logging.info("[SPOTIFYAPI] SpotifyAPI init")
        self.client_id = "cdf4ed28ce6242c79dae19287a545c4b"
        self.client_secret = "794b355f9e6d4f7285ed476ee6108125"
        self.credentials = self.get_credentials()
        self.spotify = spotipy.Spotify(client_credentials_manager=self.credentials)

    # login
    def get_credentials(self):
        logging.info(f"[SPOTIFYAPI] Returning Credentials")
        return SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret)

    # get name of playlist
    def get_playlist_name(self, url):
        logging.info(f"[SPOTIFYAPI] Returning Playlist Name")
        return self.spotify.playlist(url, fields='name')['name']

    # get artwork url
    def get_img_url(self, song):
        logging.info(f"[SPOTIFYAPI] Returning Image Url")
        try:
            img_url = song['track']['album']['images'][0]['url']
        except Exception:
            logging.warning(f"[SPOTIFYAPI] Image Url not found")
            img_url = None
        return img_url

    # get first genre of first artist
    def get_genre(self, song):
        logging.info(f"[SPOTIFYAPI] Trying to Get Genre")
        try:
            # get artist ID
            urn = song['track']['artists'][0]['uri']

            # get artist
            artist = self.spotify.artist(urn)


            # get genre
            genre = artist["genres"][0]

        except Exception as e:
            logging.warning(f"[SPOTIFYAPI] Genre not found {e}")
            genre = None

        return genre

    # get tracks from playlist
    def get_playlist_tracks(self, url):
        logging.info(f"[SPOTIFYAPI] Getting Playlist Tracks")
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

            # get year
            try:
                year = song['track']['album']['release_date'].split('-')[0]
            except:
                year = None


            artists = []
            for artist in song['track']['artists']:
                artists.append(artist['name'])

            logging.info(f"[SPOTIFYAPI] Found Track [name={name}, artists={artists}, genre={genre}, artwork_url={img_url}, year={year}]")
            tracks.append(Track(name=name, artists=artists, genre=genre, artwork_url=img_url, year=year))

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

