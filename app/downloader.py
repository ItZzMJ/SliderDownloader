import random
import string
import shutil
from mutagen.mp3 import HeaderNotFoundError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from time import sleep
from page import SearchPage
import wget
import os
import music_tag


class Downloader:
    def __init__(self, output_dir, show_chrome=False):
        # ua = UserAgent(verify_ssl=False).random
        # resolutions = ["1920,1080", "1280,1024", "1600,1200", "1680,1050", "1900,1200", "1366,768", "1440,900",
        #                "1280,800", "1536,864", "1280,720", "1024,768"]
        # res = random.choice(resolutions)
        # print(ua, res)

        self.output_dir = output_dir
        self.artwork_dir = os.path.join(output_dir, "artworks")
        if not os.path.isdir(self.artwork_dir):
            os.mkdir(self.artwork_dir)

        self.debug = []

        # set chrome options
        options = webdriver.ChromeOptions()
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--incognito")
        # options.add_argument("--user-agent=" + ua)
        # options.add_argument("--window-size=" + res)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-dev-shm-usage')

        # set output directory
        # prefs = {"download.default_directory": output_dir}
        # options.add_experimental_option("prefs", prefs)

        # show browser doing its magic
        if not show_chrome:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

        # disable Webdriver Manager output
        os.environ['WDM_LOG_LEVEL'] = '0'

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        self.driver.set_window_position(2000, 0)
        self.driver.maximize_window()

        self.url = "https://slider.kz/"
        print("Setup complete")
        self.debug.append("Setup complete")

    # download tracks
    def download(self, tracks, progress_bar=None):
        i = 0
        for track in tracks:
            i += 1
            try:
                self.download_track(track)
                if progress_bar:
                    progress_bar.update_bar((i/len(tracks)*1000))
            except NameError as err:
                print("[ERR] NAME ERROR:", end=' ')
                print(err)
                self.debug.append(f"[ERR] NAME ERROR: {err}")

                self.driver.get(self.url)
                # sleep(5)
                continue

        shutil.rmtree(self.artwork_dir)
        return self.debug

    # download one track
    def download_track(self, track):
        driver = self.driver

        # build query url and encode it
        url = self.url + "#" + urllib.parse.quote(", ".join(track.artists) + " " + track.name)
        driver.get(url)
        driver.refresh()  # refresh in case site gets stuck on a not found song

        search_page = SearchPage(self.driver)

        # hide popup
        search_page.hide_popup()

        # get download link
        print("[LOG] Getting Download link")
        self.debug.append("[LOG] Getting Download link")
        dl_link = search_page.get_dl_link()

        # download_file
        print("[LOG] Downloading " + track.print_filename())
        self.debug.append("[LOG] Downloading " + track.print_filename())
        filename = wget.download(dl_link, out=self.output_dir, bar=False)

        # download artwork
        print("[LOG] Downloading artwork")
        self.debug.append("[LOG] Downloading artwork")
        artwork = self.get_artwork(track)

        # set metadata and rename file
        print("[LOG] Setting metadata")
        self.debug.append("[LOG] Setting metadata")
        self.set_metadata(track, filename, artwork)

        print(f"[LOG] {track.print_filename()} finished!")
        self.debug.append(f"[LOG] {track.print_filename()} finished!")
        return track.print_filename()

    # set metadata of mp3 like title, artist, etc.
    def set_metadata(self, track, filename, artwork_file=None):
        file = os.path.join(self.output_dir, filename)
        # set metadata
        try:
            mp3 = music_tag.load_file(file)
            mp3['title'] = track.name
            mp3['artist'] = ", ".join(track.artists)
            mp3['genre'] = track.genre
            mp3['year'] = track.year

            # read artwork as bytes
            with open(artwork_file, 'rb') as img_in:
                mp3['artwork'] = img_in.read()
            # save metadata
            mp3.save()

        # delete corrupted mp3's
        except HeaderNotFoundError as err:
            print("[ERR] Corrupted MP3!! deleting...:" + track.print_filename())
            self.debug.append("[ERR] Corrupted MP3!! deleting...:" + track.print_filename())
            #os.remove(file)

        self.rename_file(track, filename)

    # download and rename artwork
    def get_artwork(self, track):
        artwork = wget.download(track.artwork_url, out=self.artwork_dir, bar=False)
        artwork_file = os.path.join(self.artwork_dir, artwork)
        new_artwork_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        new_artwork_file = os.path.join(self.artwork_dir, new_artwork_filename + ".jpg")
        os.rename(artwork_file, new_artwork_file)

        return new_artwork_file

    # rename file
    def rename_file(self, track, filename):
        file = os.path.join(self.output_dir, filename)
        new_filename = track.print_filename()
        new_file = os.path.join(self.output_dir, new_filename)
        os.rename(file, new_file)

    def tear_down(self):
        self.driver.quit()


