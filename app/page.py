import random
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from time import sleep
from locator import SearchPageLocators, FreeDownloadSearchPageLocators
from selenium.webdriver.support import expected_conditions as EC
import re
import logging


class BasePage(object):
    """Base class to initialize the base page that will be called from all
    pages"""

    def __init__(self, driver):
        logging.info(f"[BasePage] Page init")
        self.driver = driver

    def hide_popup(self):
        logging.info(f"[BasePage] Hiding Popup")
        driver = self.driver
        driver.execute_script("hideDisc()")

        # try:
        #     elem = WebDriverWait(driver, 5).until(
        #         lambda driver: driver.execute_script("hideDisc()"))
        # except TimeoutException:
        #     print("No Popup")


class SearchPage(BasePage):
    """Search Page, list of found Tracks"""

    def get_dl_link(self):
        driver = self.driver
        # check bitrates of songs found
        position, bitrate = self.check_bitrates()

        #print("BITRATE:")
        #print(bitrate)

        # print(f"Position: {position}")

        # find the element at the position to download
        dl_elems = driver.find_elements(*SearchPageLocators.DOWNLOAD_BUTTONS)
        dl_link = dl_elems[position].find_element(*SearchPageLocators.A_TAG)

        # return download link
        return dl_link.get_attribute("href"), bitrate

    # check bitrates of search results
    def check_bitrates(self):
        logging.info(f"[SearchPage] Checking Bitrates")
        driver = self.driver

        elems = WebDriverWait(driver, 5).until(
            lambda driver: driver.find_elements(*SearchPageLocators.TRACK_TIME))

        i = 0

        highest_bitrate_position = 0  # listposition of song with highest bitrate
        highest_bitrate = 0

        # iterate through found dl links and check bitrates
        for elem in elems:
            # check if
            if "Invalid" in elem.text:
                raise NameError("Song not found!")

            # show informer
            script = elem.get_attribute("onclick")
            # print(f"Executing Script: {script}")
            driver.execute_script(script)  # TODO: maybe just check downloadlink for extra != null ?

            #logging.info("Executed Script")

            # wait till informer element is completly loaded
            try:
                WebDriverWait(driver, 4).until(  # until '<img src="/media/images/preload.gif">' is away
                    EC.text_to_be_present_in_element(SearchPageLocators.INFORMER, "Bitrate"))
                    #EC.invisibility_of_element_located(SearchPageLocators.PRELOADER))
            except TimeoutException:
                i += 1
                continue  # if Informer stays empty check next element

            sleep(0.1)
            bitrate_elem = driver.find_element(*SearchPageLocators.INFORMER)

            if not bitrate_elem.text:  # if informer is empty
                continue

            # extract bitrate
            bitrate = int(re.search(r'\d+', bitrate_elem.text.split(":")[1]).group(0))

            #logging.info("ExtractingBitrate")


            if bitrate < 319: # some tracks are shown with 319 kbit/s ?
                if bitrate > highest_bitrate:
                    highest_bitrate_position = i
                    highest_bitrate = bitrate

                i += 1
                continue
            else:
                return i, 320

        #logging.info(f"Bitrate: {highest_bitrate}")

        print(f"Can't find a Track with 320 kbit/s, highest bitrate was {highest_bitrate}")

        return highest_bitrate_position, highest_bitrate


class FreeDownloadSearchPage(BasePage):
    """Free Download Search Page, search for a song"""

    def search(self, query):
        driver = self.driver

        try:

            # type query
            input = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.INPUT))

            input.clear()
            sleep(random.randint(200, 1500)/1000)

            input.send_keys(query)
            sleep(random.randint(1000, 3000)/1000)

            # click search button
            search_button = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.SEARCH_BUTTON))

            search_button.click()


            # check results
            try:
                no_results = WebDriverWait(driver, 5).until(
                    lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.NO_RESULT))
            except TimeoutException:
                return True
            else:
                return False

        except Exception as e:
            print("[ERR] ")
            print(e)
            return False

    def use_vpn(self):
        driver = self.driver

        # check if checkbox is already checked
        try:
            checkbox = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.USE_VPN_CHECKBOX))
            if not checkbox.is_selected():
                checkbox.click()

        except Exception as e:
            print("[ERR] ")
            print(e)

    def get_dl_link(self):
        driver = self.driver

        try:
            dl_link = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.FIRST_RESULT_DL_BUTTON))

            dl_link.click()
            print(f"[LOG] Clicked Download Button")

            sleep(random.randint(1000, 3000) / 1000)

            return True


        except Exception as e:
            print("[ERR] ")
            print(e)
            return False

    def check_captcha(self):
        driver = self.driver

        try:
            captcha = WebDriverWait(driver, 3).until(
                lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.CAPTCHA))
        except TimeoutException:
            return False
        else:
            return True

    def solve_captcha(self):
        driver = self.drover

    def download(self):
        driver = self.driver

        try:
            dl_button = WebDriverWait(driver, 5).until(
                lambda driver: driver.find_element(*FreeDownloadSearchPageLocators.DL_BUTTON))

            sleep(random.randint(1000, 3000)/1000)

            dl_button.click()

            sleep(random.randint(1000, 3000)/1000)

            return True

        except Exception as e:
            print("[ERR] ")
            print(e)
            return False
