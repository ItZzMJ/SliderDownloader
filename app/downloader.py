import random
import string
import shutil
from mutagen.mp3 import HeaderNotFoundError
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
from page import SearchPage, FreeDownloadSearchPage
import os
import music_tag
import urllib.request
import ssl
import logging
from time import sleep

class Downloader:
    def __init__(self, output_dir, show_chrome=False):
        logging.info("[DOWNLOADER] Downloader init")
        # ua = UserAgent(verify_ssl=False).random
        # resolutions = ["1920,1080", "1280,1024", "1600,1200", "1680,1050", "1900,1200", "1366,768", "1440,900",
        #                "1280,800", "1536,864", "1280,720", "1024,768"]
        # res = random.choice(resolutions)
        # print(ua, res)

        self.output_dir = output_dir
        self.artwork_dir = os.path.join(output_dir, "artworks")
        if not os.path.isdir(self.artwork_dir):
            os.mkdir(self.artwork_dir)

        #self.debug = []

        # set chrome options
        options = webdriver.ChromeOptions()
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        #options.add_argument("--incognito")
        # options.add_argument("--user-agent=" + ua)
        # options.add_argument("--window-size=" + res)
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-dev-shm-usage')

        # load adBlocker
        options.add_extension("./extension/uBlockOrigin.crx")

        # set output directory
        prefs = {"download.default_directory": output_dir}
        options.add_experimental_option("prefs", prefs)

        # show browser doing its magic
        # if not show_chrome:
        #     options.add_argument("--headless")
        #     options.add_argument("--disable-gpu")

        # disable Webdriver Manager output
        os.environ['WDM_LOG_LEVEL'] = '0'

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        self.driver.set_window_position(2000, 0)
        self.driver.maximize_window()

        self.url = "https://slider.kz/"
        self.not_found = []
        self.low_bitrate = []
        print("[LOG] Setup complete")
        logging.info("[DOWNLOADER] Setup complete")
        #self.debug.append("[LOG] Setup complete")

    # download tracks
    def download(self, tracks, progress_bar=None):
        logging.info(f"[DOWNLOADER] Starting to download {len(tracks)} Tracks")
        i = 0
        for track in tracks:
            i += 1
            try:
                self.download_track_new(track)
                if progress_bar:
                    progress_bar.update_bar((i/len(tracks)*1000))
            except NameError as err:
                logging.error(f"[DOWNLOADER] Name Error: {err}")
                print("[ERR] NAME ERROR:", end=' ')
                print(err)
                #self.debug.append(f"[ERR] NAME ERROR: {err}")

                # logging.error("append to array")

                if track.purchase_url:
                    self.not_found.append(f"{track.print_artists()} - {track.name} ({track.purchase_url})")
                else:
                    self.not_found.append(f"{track.print_artists()} - {track.name}")
                # logging.error("successfully appended to array")

                self.driver.get(self.url)
                # sleep(5)
                continue

        shutil.rmtree(self.artwork_dir)

        return self.not_found, self.low_bitrate

    # download one track
    def download_track(self, track):
        logging.info(f"[DOWNLOADER] Starting Download for {track.print_filename()}")
        driver = self.driver

        # build query url and encode it
        url = self.url + "#" + urllib.parse.quote(track.print_artists() + " " + track.name)

        driver.get(url)
        driver.refresh()  # refresh in case site gets stuck on a not found song

        search_page = SearchPage(self.driver)

        # hide popup
        search_page.hide_popup()

        # get download link
        print(f"[LOG] Getting Download link for {track.print_artists()} - {track.name}")
        # self.debug.append(f"[LOG] Getting Download link for {track.print_artists()} - {track.name}")
        logging.info(f"[LOG] Getting Download link for {track.print_artists()} - {track.name}")

        dl_link, bitrate = search_page.get_dl_link()

        #print(f"BITRATE: {bitrate}")
        if bitrate < 319:
            self.low_bitrate.append(f"{track.print_artists()} - {track.name}")

        # download_file
        print("[LOG] Downloading " + track.print_filename())
        # self.debug.append("[LOG] Downloading " + track.print_filename())
        logging.info("[DOWNLOADER] Downloading " + track.print_filename())
        filename = os.path.join(self.output_dir, track.print_filename())
        # filename = wget.download(dl_link, out=self.output_dir, bar=False)

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        r = urllib.request.urlopen(dl_link, context=ctx)
        # print(r.getcode())
        with open(filename, "wb") as f:
            f.write(r.read())

        # download artwork
        print(f"[LOG] Downloading artwork for {track.print_artists()} - {track.name}")
        # self.debug.append(f"[LOG] Downloading artwork for {track.print_artists()} - {track.name}")
        logging.info(f"[DOWNLOADER] Downloading artwork for {track.print_artists()} - {track.name}")
        artwork = self.get_artwork(track)

        # set metadata and rename file
        print("[LOG] Setting metadata")
        # self.debug.append("[LOG] Setting metadata")
        logging.info("[DOWNLOADER] Setting metadata")
        self.set_metadata(track, filename, artwork)

        print(f"[LOG] {track.print_filename()} finished!")
        # self.debug.append(f"[LOG] {track.print_filename()} finished!")
        logging.info(f"[DOWNLOADER] {track.print_filename()} finished!")
        return track.print_filename()

    def download_track_new(self, track):
        logging.info(f"[DOWNLOADER] Starting Download for {track.print_filename()}")
        driver = self.driver

        url = "https://free-mp3-download.net/"

        driver.get(url)
        sleep(2)

        search_page = FreeDownloadSearchPage(self.driver)

        search_page.use_vpn()

        query = track.print_artists() + " - " + track.name

        success = search_page.search(query)

        # if search is not successful, sanitize query from (Original Mix) (Extended Mix) [HEK003] etc.
        if not success:
            to_replace = [
                "(Original Mix)",
                "(Extended Mix)",
                "(Preview)",
                "(Out Now)"
                "[", # label shit
            ]
            for replace in to_replace:
                query = query.split(replace)[0].strip()

            success = search_page.search(query)

        if not success:
            if track.purchase_url:
                self.not_found.append(f"{track.print_artists()} - {track.name} ({track.purchase_url})")
            else:
                self.not_found.append(f"{track.print_artists()} - {track.name}")
            return

        # get download link
        print(f"[LOG] Getting Download link for {track.print_artists()} - {track.name}")

        sleep(random.randint(1000, 3000)/1000)
        dl_link = search_page.get_dl_link()
        sleep(random.randint(1000, 3000)/1000)


        if not dl_link:
            print(f"[ERR] No download link found for {track.print_artists()} - {track.name}")
            if track.purchase_url:
                self.not_found.append(f"{track.print_artists()} - {track.name} ({track.purchase_url})")
            else:
                self.not_found.append(f"{track.print_artists()} - {track.name}")
            return

        # download_file
        print(f"[LOG] Downloading Track {track.print_artists()} - {track.name}")

        sleep(random.randint(1000, 3000) / 1000)

        # check for captcha
        if search_page.check_captcha():
            search_page.solve_captcha()

            # user input required
            print("[LOG] Captcha detected, please solve it in the next 10 seconds")
            sleep(10)
            print("[LOG] Continuing..")

        # click download button
        if not search_page.download():
            if track.purchase_url:
                self.not_found.append(f"{track.print_artists()} - {track.name} ({track.purchase_url})")
            else:
                self.not_found.append(f"{track.print_artists()} - {track.name}")


        return

    # set metadata of mp3 like title, artist, etc.
    def set_metadata(self, track, filename, artwork_file=None):
        file = os.path.join(self.output_dir, filename)
        # set metadata
        try:
            mp3 = music_tag.load_file(file)
            mp3['title'] = track.name
            mp3['artist'] = track.print_artists()
            mp3['genre'] = track.genre
            mp3['year'] = track.year

            # read artwork as bytes
            if artwork_file:
                with open(artwork_file, 'rb') as img_in:
                    mp3['artwork'] = img_in.read()
                # save metadata
                mp3.save()

        # delete corrupted mp3's
        except HeaderNotFoundError as err:
            print("[ERR] Corrupted MP3!! deleting...:" + track.print_filename())
            #self.debug.append("[ERR] Corrupted MP3!! deleting...:" + track.print_filename())
            logging.error("[DOWNLOADER] Corrupted MP3!! deleting...:" + track.print_filename())
            #os.remove(file)

        self.rename_file(track, filename)

    # download artwork
    def get_artwork(self, track):
        try:
            artwork_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            artwork_file = os.path.join(self.artwork_dir, artwork_filename + ".jpg")
            r = urllib.request.urlopen(track.artwork_url, context=ssl.create_default_context())
            # print(r.getcode())
            with open(artwork_file, "wb") as f:
                f.write(r.read())

        except Exception:
            print("[ERR] Artwork not found")
            #self.debug.append("[ERR] Artwork not found")
            logging.warning("[DOWNLOADER] Artwork not found")
            return None

        return artwork_file

    # rename file
    def rename_file(self, track, filename):
        logging.info("[DOWNLOADER] Renaming File")
        file = os.path.join(self.output_dir, filename)
        new_filename = track.print_filename()
        new_file = os.path.join(self.output_dir, new_filename)
        os.rename(file, new_file)

    def tear_down(self):
        self.driver.quit()


