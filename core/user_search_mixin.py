from selenium.common.exceptions import TimeoutException
from urllib.parse import quote
from core.base import BaseLinkedinBot
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


class UserSearchMixin(BaseLinkedinBot):
    
    LOCATION_GEO_URNS = {
        "Israel": "101620260",
        "United States": "103644278",
        "United Kingdom": "101165590",
        "Canada": "101174742",
    }
    
    def build_search_url(self, keyphrase, location="Israel", startpage=None, first=False, second=True, third=True):
        geo_urn = self.LOCATION_GEO_URNS.get(location, "101620260")
        
        network_filters = []
        if second:
            network_filters.append("%22S%22")
        if third:
            network_filters.append("%22O%22")
        if first:
            network_filters.append("%22F%22")
        
        network_param = "%5B" + "%2C".join(network_filters) + "%5D"
        
        url = f"https://www.linkedin.com/search/results/people/?geoUrn=%5B%22{geo_urn}%22%5D&keywords={quote(keyphrase)}&network={network_param}&origin=FACETED_SEARCH"
        
        if startpage and int(startpage) > 0:
            url += f"&page={startpage}"
        
        return url
    
    def search(self, keyphrase, startpage, browser, location, first=False, second=True, third=True):
        search_url = self.build_search_url(keyphrase, location, startpage, first, second, third)
        self.log(f"Navigating to search URL: {search_url}")
        browser.get(search_url)
        self.random_wait(3, 5)

    def get_name_title(self, element):
        try:
            name_title = element.find_element(By.XPATH,
                                              ".//a[contains(@data-test-app-aware-link)]/span/span[@aria-hidden='true']").text
        except:
            name_title = element.find_element(By.XPATH,
                                              ".//a[@data-test-app-aware-link]/span/span[@aria-hidden='true']").text

        return name_title

    def get_profile_link(self, element):
        try:
            anchor_element = element.find_element(By.XPATH, ".//a[contains(@data-test-app-aware-link)]")
        except:
            anchor_element = element.find_element(By.XPATH, ".//a[@data-test-app-aware-link]")
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
