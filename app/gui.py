import PySimpleGUI as sg
import logging


class GUI:
    def __init__(self, result_dir=None, url=None):
        logging.info(f"[GUI] GUI init")
        sg.theme("Dark")

        dir_input = [
            sg.Text("Zielordner auswählen"),
            sg.In(size=(90, 10), enable_events=True, key="-FOLDER-", default_text=result_dir),
            sg.FolderBrowse()
        ]

        link_input = [
            sg.Text("Playlistlink eingeben"),
            sg.In(size=(90, 10), enable_events=True, key="-LINK-", default_text=url),
        ]

        output = [
            sg.Output(size=(110, 30), background_color='white', text_color='black', key='-OUTPUT-')
        ]

        sg.SetOptions(progress_meter_color=('green', 'white'))
        progress_bar = [
            sg.ProgressBar(1000, orientation='h', size=(72, 20), key='-PROGRESS BAR-')
        ]

        buttons = [
            sg.Button('Exit'),
            sg.Checkbox('show Chrome', pad=((550, 0), 0), default=False, key='-SHOWCHROME-'),
            sg.Button('Download', pad=((50, 0), 0)),
        ]

        self.layout = [
            [dir_input],
            [link_input],
            [output],
            [progress_bar],
            [buttons]
        ]

    def get_layout(self):
        logging.info(f"[GUI] Returning Layout")
        return self.layout


# top_window = sg.Window('Slider Downloader', layout)
#
# while True:
#     event, values = top_window.read()
#     if event == "Exit" or event == sg.WINDOW_CLOSED:
#         break
#
# top_window.close()
# window_background.close()

