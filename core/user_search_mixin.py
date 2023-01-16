from selenium.common.exceptions import TimeoutException

from core.base import BaseLinkedinBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


class UserSearchMixin(BaseLinkedinBot):
    def search(self, keyphrase, startpage, browser, location, first=False, second=True, third=True):
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
        searchbox = WebDriverWait(browser, 10).until(element_present)
        searchbox.clear()
        searchbox.send_keys(keyphrase)
        self.random_wait(2, 4)
        searchbox.send_keys(Keys.ENTER)
        self.random_wait(2, 4)
        counter = 0

        while counter < 2:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//button[text()='People']"))
                people_button = WebDriverWait(browser, 10).until(element_present)
                people_button.click()
                counter = 2
            except TimeoutException:
                if counter == 0:
                    self.error_handler()
                    counter += 1
                    continue
                if counter > 0:
                    self.log("Timed out waiting for page to load", error=self.get_error())
                    return -1
        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//button[text()='Locations']"))
            location_button = WebDriverWait(browser, 10).until(element_present)
            location_button.click()
        except TimeoutException as e:
            self.log("Timed out waiting for page to load", error=self.get_error())
            return -1
        try:
            element_present = EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Add a location']"))
            israel_input = WebDriverWait(browser, 10).until(element_present)
            israel_input.send_keys(location)

        except TimeoutException as e:
            self.log("cant send keys")

        try:
            element_present = EC.presence_of_element_located(
                (By.XPATH, f"//div[@role='option']//*/span[text()='{location}']/.."))

            israel_button = WebDriverWait(browser, 10).until(element_present)
            israel_button.click()
        except Exception:
            try:
                element_present = EC.presence_of_element_located(
                    (By.XPATH, f"//span[text()='{location}']/.."))
                israel_button2 = WebDriverWait(browser, 10).until(element_present)
                israel_button2.click()
            except Exception as e:
                self.log("Timed out waiting for page to load", error=self.get_error())
                return -1
        self.random_wait(5, 7)
        location_button.click()
        if first or second or third:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//button[text()='Connections']"))
                connections_button = WebDriverWait(self.browser, 10).until(element_present)
                self.click_button_humanly(connections_button)
            except TimeoutException:
                self.log("Timed out waiting for page to load")
                return -1
        if first:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, ".//span[text()='1st']"))
                first_button = WebDriverWait(self.browser, 10).until(element_present)
                first_button.click()
            except TimeoutException as e:
                self.log("Timed out waiting for page to load", error=self.get_error())
                return -1
        if second:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//span[text()='2nd']"))
                second_button = WebDriverWait(self.browser, 10).until(element_present)
                self.click_button_humanly(second_button)
            except TimeoutException as e:
                self.log("Timed out waiting for page to load", error=self.get_error())
                return -1
        if third:
            try:
                element_present = EC.presence_of_element_located((By.XPATH, "//span[text()='3rd+']"))
                third_button = WebDriverWait(self.browser, 10).until(element_present)
                self.click_button_humanly(third_button)
            except TimeoutException as e:
                self.log("Timed out waiting for page to load", error=self.get_error())
                return -1
        self.random_wait()
        self.click_button_humanly(connections_button)

        self.random_wait(2, 4)
        start_page = self.config.get('start_page', startpage)

        if start_page:
            if int(start_page) > 0:
                url = browser.current_url
                browser.get(url + "&page=" + str(start_page))

    def get_name_title(self, element):
        try:
            name_title = element.find_element(By.XPATH,
                                              ".//a[contains(@class, 'app-aware-link')]/span/span[@aria-hidden='true']").text
        except:
            name_title = element.find_element(By.XPATH,
                                              ".//a[@class='app-aware-link ']/span/span[@aria-hidden='true']").text

        return name_title

    def get_profile_link(self, element):
        try:
            anchor_element = element.find_element(By.XPATH, ".//a[contains(@class, 'app-aware-link')]")
        except:
            anchor_element = element.find_element(By.XPATH, ".//a[@class='app-aware-link ']")
        url = anchor_element.get_attribute('href')
        return url

    def scroll_to_bottom(self):
        self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def get_next_button(self):
        self.scroll_to_bottom()
        element_present = EC.presence_of_element_located(
            (By.XPATH, ".//button[contains(@class, 'artdeco-pagination__button')][contains(., 'Next')]"))
        try:
            next_button = WebDriverWait(self.browser, 30).until(element_present)
            return next_button
        except Exception as err:
            self.log(err)
            raise err
