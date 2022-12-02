from selenium.webdriver.common.by import By


class SearchPageLocators(object):
    POPUP = (By.CSS_SELECTOR, "#fullwrapper > div")
    DOWNLOAD_BUTTONS = (By.CLASS_NAME, "trackDownload")
    TRACK_TIME = (By.CLASS_NAME, "trackTime")
    INFORMER = (By.ID, "informer")
    A_TAG = (By.TAG_NAME, "a")
    PRELOADER = (By.CSS_SELECTOR, "#informer > img")


class FreeDownloadSearchPageLocators(object):
    INPUT = (By.ID, "q")
    SEARCH_BUTTON = (By.ID, "snd")
    USE_VPN_CHECKBOX = (By.XPATH, '//*[@id="search"]/div[3]/label')
    NO_RESULT = (By.XPATH, '//*[@id="results"]/span')
    FIRST_RESULT_DL_BUTTON = (By.XPATH, '//*[@id="results_t"]/tr/td[3]/a')
    CAPTCHA = (By.ID, "captcha")
    DL_BUTTON = (By.XPATH, '/html/body/main/div/div/div/div/div[3]/button')


