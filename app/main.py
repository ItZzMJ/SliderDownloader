import json
import traceback
from json import JSONDecodeError
from spotifyAPI import SpotifyAPI
from soundcloudAPI import SoundcloudAPI
from downloader import Downloader
import os
import threading
import PySimpleGUI as sg
import logging
from sys import exit


LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="LOG.log", level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()


class Main:
    def __init__(self):
        logging.info("[MAIN] Starting Application")
        self.url = "https://open.spotify.com/playlist/3rAF2TSX5OEaizE6o8op34?si=59c270ab42004510"
        #self.debug = []
        self.show_chrome = False
        self.save_debug = False

    def loop(self):
        logging.info("[MAIN] Starting Loop")
        settings = self.load_settings()
        output_dir = settings['result_dir']
        url = settings['url']

        if not os.path.isfile("config.json"):
            configdata = dict()
            configdata["soundcloud"] = {
                "client_id": "lfCwve78235Iw2UNbGezTfUWMB5zHKmb"
            }
            configdata["spotify"] = {
                "client_id": "cdf4ed28ce6242c79dae19287a545c4b",
                "client_secret": "794b355f9e6d4f7285ed476ee6108125"
            }

        with open('config.json', "w") as f:
            json.dump(configdata, f, indent=2)

        layout = self.get_layout(output_dir, url)
        window = sg.Window('Slider Downloader v1.3', layout)

        # Main Loop
        try:
            while True:
                event, values = window.read()  # read events

                # exit button clicked
                if event == sg.WINDOW_CLOSED or event == 'Exit':
                    logging.info("[MAIN] Exiting Application")
                    exit(0)

                # download button clicked
                elif event == 'Download':
                    logging.info("[MAIN] Download Button pressed")
                    window['-OUTPUT-'].Update('')

                    # check if output directory is set
                    if not values['-FOLDER-']:
                        logging.error("[MAIN] Kein Zielordner angegeben!")
                        print("[ERR] Keinen Zielordner angegeben!")
                        # self.debug.append("[ERR] Keinen Zielordner angegeben!")

                    # check if playlist url is set
                    elif not values['-LINK-']:
                        logging.error("[MAIN] Kein Link angegeben!")
                        print("[ERR] Keinen Playlistlink angegeben!")
                        # self.debug.append("[ERR] Keinen Playlistlink angegeben!")

                    # if all tests pass, start download
                    else:
                        self.show_chrome = values['-SHOWCHROME-']
                        output_dir = values['-FOLDER-']
                        url = values['-LINK-']

                        logging.info(f"[MAIN] Saving Settings [output_dir: {output_dir}, url: {url}, showchrome: {self.show_chrome}]")

                        self.save_settings(output_dir, url)

                        # start download
                        try:
                            progress_bar = window['-PROGRESS BAR-']

                            logging.info("[MAIN] Starting Download Thread")
                            # start thread
                            thread = threading.Thread(target=self.run, args=(url, output_dir, progress_bar), daemon=True)
                            thread.start()
                            logging.info("[MAIN] Thread started successfully")
                            #self.run(url, output_dir, progress_bar)

                        except Exception as e:
                            logging.error(f"[MAIN] {e}")
                            print(f"[ERR] {e}")
                            tb = traceback.format_exc()
                            #self.debug.append(tb)
                            logging.error(f"[MAIN] {tb}")




                        # self.save_settings(self.result_dir, self.url)

                        # self.progress_bar = window['-PROGRESS BAR-']

                        # songs = self.get_songs(self.url)

                        # downloaded_tracks = self.check_dir(self.dl_path)

                        # song_count = len(songs) - len(downloaded_tracks)

                        # self.progress_bar.update_bar(1, song_count*2)

        except Exception as e:
            tb = traceback.format_exc()
            #self.debug.append(tb)
            logging.error(f"[MAIN] {tb}")

        finally:
            logging.info("[MAIN] Exiting..")
            print("[LOG] Exiting..")
            #self.debug.append("[LOG] Exiting..")
            window['-OUTPUT-'].__del__()
            window.close()
            #if self.save_debug:
            #    self.print_debug()

    def run(self, url, output_dir, progress_bar=None):
        # set configs through gui
        # output_dir = os.path.join(pathlib.Path().resolve(), "music")

        # get Tracks
        try:
            print("[LOG] Getting Tracks")
            #self.debug.append("[LOG] Getting Tracks")
            logging.info("[MAIN] Getting Tracks")
            tracks = self.get_tracks(url)

        except Exception as e:
            print(f"[ERR] {e}")
            tb = traceback.format_exc()
            # self.debug.append(tb)
            logging.error(f"[MAIN] {e}")
            logging.error(f"[MAIN] {tb}")
            exit(-1)

        else:
            if tracks is not None:
                logging.info("[MAIN] Getting Playlist Name")
                # get playlist name
                playlist_name = self.get_playlist_name(tracks, url)
                playlist_dir = os.path.join(output_dir, playlist_name)

                # make directory for playlist download if doesnt exist already
                if not os.path.isdir(playlist_dir):
                    print(f"[LOG] Creating {playlist_dir}")
                    #self.debug.append(f"[LOG] Creating {playlist_dir}")
                    logging.info(f"[MAIN] Creating Playlist Dir {playlist_dir}")
                    os.mkdir(playlist_dir)

                # check for existing tracks if directory exists
                else:
                    tracks = self.filter_existing_tracks(playlist_dir, tracks)

                # for track in tracks:
                #     print(track.print_artists())
                # exit(0)

                if tracks:
                    # download Tracks
                    self.download(tracks, playlist_dir, progress_bar)

                # if tracks is empty
                else:
                    print("[ERR] No new Tracks found!")
                    logging.warning(f"[MAIN] No new Tracks found!")
                    #self.debug.append("[ERR] No new Tracks found!")

    # get name of playlist
    def get_playlist_name(self, tracks, url):
        if "soundcloud" in url:
            logging.info(f"[MAIN] Getting Playlist Name from Soundcloud")
            soundcloud = SoundcloudAPI()

            # get Name
            return soundcloud.get_playlist_name(url)

        elif "spotify" in url:
            logging.info(f"[MAIN] Getting Playlist Name from Spotify")
            spotify = SpotifyAPI()

            # get Name
            return spotify.get_playlist_name(url)

    # save output_dir and url
    def save_settings(self, result_dir, url):
        logging.info(f"[MAIN] Saving Settings file")
        file = "slider_settings.json"

        #if os.path.isfile(file):
        #    os.remove(file)

        settings = {'result_dir': result_dir, 'url': url}

        with open(file, "w") as f:
            json.dump(settings, f)

    # load previous output_dir and url
    def load_settings(self):
        logging.info(f"[MAIN] Load Settings file")
        file = "slider_settings.json"
        if not os.path.isfile(file):
            return {'result_dir': '', 'url': ''}

        try:
            with open(file, "r") as f:
                settings = json.load(f)
        except JSONDecodeError as e:
            print("[ERR] Error while reading settings! Check file!")
            logging.error("[MAIN] Error while reading settings! Check file!")
            logging.error(f"[MAIN] Error: {e}")

            settings = {'result_dir': '', 'url': ''}

        return settings

    # get Layout for GUI
    def get_layout(self, result_dir=None, url=None):
        logging.info(f"[MAIN] Getting Layout")
        sg.theme("Dark")

        dir_input = [
            sg.Text("Zielordner auswählen"),
            sg.In(size=(90, 10), enable_events=True, key="-FOLDER-", default_text=result_dir),
            sg.FolderBrowse()
        ]

        link_input = [
            sg.Text("Playlistlink eingeben "),
            sg.In(size=(90, 10), enable_events=True, key="-LINK-", default_text=url),
        ]

        output = [
            sg.Output(size=(120, 30), background_color='white', text_color='black', key='-OUTPUT-')
        ]

        sg.SetOptions(progress_meter_color=('green', 'white'))
        progress_bar = [
            sg.ProgressBar(1000, orientation='h', size=(78, 20), key='-PROGRESS BAR-')
        ]

        buttons = [
            sg.Button('Exit'),
            sg.Checkbox('I wanna see the magic happening', pad=((450, 0), 0), default=False, key='-SHOWCHROME-'),
            sg.Button('Download', pad=((50, 0), 0)),
        ]

        layout = [
            [dir_input],
            [link_input],
            [output],
            [progress_bar],
            [buttons]
        ]
        return layout

    # check for songs in directory to prevent double downloading
    def filter_existing_tracks(self, playlist_dir, tracks):
        logging.info(f"[MAIN] Filter existing Tracks")
        erg = []
        for track in tracks:
            # if Track does not exist already, save it in erg
            if not os.path.isfile(os.path.join(playlist_dir, track.print_filename())):
                erg.append(track)
            else:
                print(f"[LOG] {track.print_filename()} exists already and will not be downloaded.")
                logging.info(f"[MAIN] {track.print_filename()} exists already and will not be downloaded.")
                #self.debug.append(f"[LOG] {track.print_filename()} exists already and will not be downloaded.")

        return erg

    # def print_debug(self):
    #     # os.remove("debug.txt")
    #     i = 0
    #     with open("debug.txt", "w") as f:
    #         for message in self.debug:
    #             print("[" + str(i) + "] " + message)
    #             f.write("[" + str(i) + "] " + message + "\n")
    #             i += 1

    def get_tracks(self, url):
        # determine if soundcloud or spotify
        if "soundcloud" in url:
            logging.info(f"[MAIN] Fetching Tracks from Soundcloud")
            soundcloud = SoundcloudAPI()

            # get Tracks
            return soundcloud.get_playlist_tracks(url)

        elif "spotify" in url:
            logging.info(f"[MAIN] Fetching Tracks from Spotify")
            spotify = SpotifyAPI()

            # get Tracks
            return spotify.get_playlist_tracks(url)

        else:
            logging.error(f"[MAIN] Wrong Link used {url}")
            raise Exception("Soundcloud oder Spotify URL plsss")

    # Threading function for downloading
    def download(self, tracks, playlist_dir, progress_bar=None):
        logging.info(f"[MAIN] Creating Downloader")
        downloader = Downloader(playlist_dir, self.show_chrome)
        try:
            logging.info(f"[MAIN] Trying Download")
            downloader.download(tracks, progress_bar)
        finally:
            downloader.tear_down()

        #self.debug.extend(download_log)

        # try:
        #     f = open("download_log.txt", "w")
        #     f.write(*download_log)
        # finally:
        #     f.close()

        print("<------------ Download Finished! Fasching Mafensen ------------>")
        logging.info("[MAIN] <------------ Download Finished! Fasching Mafensen ------------>")
        #self.debug.append("<------------ Download Finished! Fasching Mafensen ------------>")


if __name__ == "__main__":
    main = Main()
    main.loop()
    #url = "https://open.spotify.com/playlist/3rAF2TSX5OEaizE6o8op34?si=cd257ac5ed824873"
    #output_dir = "/home/jannik/code/SliderDownloader/app/music"
    #main.run(url, output_dir)
    #print("<------------ Finished! Fasching Mafensen ------------>")


