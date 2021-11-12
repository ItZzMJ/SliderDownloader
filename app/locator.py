from selenium.webdriver.common.by import By


class SearchPageLocators(object):
    POPUP = (By.CSS_SELECTOR, "#fullwrapper > div")
    DOWNLOAD_BUTTONS = (By.CLASS_NAME, "trackDownload")
    TRACK_TIME = (By.CLASS_NAME, "trackTime")
    INFORMER = (By.ID, "informer")
    A_TAG = (By.TAG_NAME, "a")
    PRELOADER = (By.CSS_SELECTOR, "#informer > img")



