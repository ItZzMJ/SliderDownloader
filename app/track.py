class Track:
    def __init__(self, name, artists, genre=None, artwork_url=None, year=None):
        self.name = name
        self.artists = artists
        self.genre = genre
        self.artwork_url = artwork_url
        self.year = year

    def get_artists(self):
        return self.artists

    def print_artists(self):
        artists = ", ".join(self.artists)
        return artists

    def print_filename(self):
        return self.print_artists() + " - " + self.name + ".mp3"

    def get_name(self):
        return self.name

    def get_genre(self):
        return self.genre

