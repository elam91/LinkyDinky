import os
import time
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from core.friend_request_core import FriendRequestBot


class WithdrawBot(FriendRequestBot):
    def __init__(self):
        super().__init__()
        if not self.config.get('withdraw_amount'):
            self.config['withdraw_amount'] = 10

    def main(self):
        start_time = time.time()
        self.create_browser()
        self.connect_to_linkedin()
        self.browser.get("https://www.linkedin.com/mynetwork/invitation-manager/sent/")
        withdrawn_users = 0
        element_present = EC.presence_of_element_located(
            (By.XPATH, "//h1[contains(., 'Manage invitations')]"))
        page_title = WebDriverWait(self.browser, 5).until(element_present)
        current_page = 0
        while withdrawn_users < self.config['withdraw_amount'] and current_page < 100:
            self.log(f"Running for {(time.time() - start_time) / 60} minutes")
            users = self.browser.find_elements(By.XPATH, "//li[contains(@class, 'invitation-card')]")
            for user in users:
                self.close_all_chats()
                time_ago = user.find_element(By.TAG_NAME, 'time').text
                if ('month' in time_ago) or ('4 weeks' in time_ago):
                    name = user.find_element(By.XPATH,
                                             ".//span[@class='invitation-card__title t-16 t-black t-bold']").text
                    withdraw_button = user.find_element(By.XPATH,
                                                        ".//button[contains(@class, 'invitation-card__action-btn')]/span[contains(., 'Withdraw')]/..")
                    withdraw_button.click()
                    self.random_wait(1, 2)
                    confirm_button = self.get_generic_linkedin_button("Withdraw")
                    confirm_button.click()
                    self.random_wait(3, 5)
                    self.log(f'{name} withdrawn, time was {time_ago}')
                    withdrawn_users += 1
                    if withdrawn_users > self.config['withdraw_amount']:
                        break
                else:
                    continue

            try:
                next_button = self.get_next_button()
                next_clickable = next_button.is_enabled()
            except:
                return -1
            try:
                self.close_all_chats()
                if next_clickable:
                    next_button.click()
            except:
                return -1
            self.random_wait(2, 4)
            self.close_all_chats()
            url = self.browser.current_url
            self.log(f"Next clickable? {next_clickable}")

            if next_clickable:
                try:
                    current_page = int(url.split('page=')[1])
                    self.log("the current page is " + str(current_page))
                except:
                    break
            else:
                self.log(f"Next clickable? {next_clickable}")
                current_page = 100
                self.log("REACHED LAST PAGE, ENDING")
        end_time = time.time()
        time_took_mins = (end_time - start_time) / 60
        self.log(f"Finished withdrawing invites, total {withdrawn_users}")
        self.prepare_discord_message(withdrawn_users, time_took_mins, current_page, None,
                                     title="Finished withdrawing invites",
                                     action="Withdrawn")
