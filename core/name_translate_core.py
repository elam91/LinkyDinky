import locale
import os
import time
from contextlib import contextmanager
from locale import getlocale, setlocale

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
import json
import random
import datetime
from pathlib import Path

from selenium.webdriver.common.by import By

from core.friend_request_core import FriendRequestBot


class NameTranslatorBot(FriendRequestBot):
    def __init__(self):
        super().__init__()

    def find_users(self):
        self.log(
            f"Starting to look for names to translate, currently there are {len(self.untranslated_names)} untranslated")

        self.close_all_chats()
        count = 0
        user_list = []
        results = self.browser.find_elements(By.XPATH, "//div[@class='entity-result__item']")
        for user in results:
            try:
                name_title = self.get_name_title(user)
            except:
                name_title = ""
                continue
            first_name = name_title.lower().split()[0]
            if first_name in self.untranslated_names or first_name in self.translated_names.keys() or first_name in self.name_blacklist:
                continue

            whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            res = 1
            for word in name_title.lower().split():
                if word in self.name_blacklist:
                    self.log(f"NAME BLACKLIST: {name_title} blacklisted name {word}, skipping")
                    res = -1
                    break
            if res == -1:
                continue

            self.untranslated_names.append(first_name)
            count += 1
            self.list_to_json(self.config_path + "untranslated_names.json", self.untranslated_names)

        self.close_all_chats()
        try:
            next_button = self.get_next_button()
        except:
            time.sleep(30)
            return (-1, -1)
        try:
            self.close_all_chats()
            next_button.click()
        except:
            time.sleep(30)
            return (-1, -1)
        self.random_wait(2, 4)
        self.close_all_chats()
        url = self.browser.current_url
        current_page = str(url.split('page=')[1].split('&')[0])
        self.log("the current page is " + current_page)
        print(f"the length of the untranslated list is {len(self.untranslated_names)}")
        return count, current_page

    def main(self):
        self.setup_for_run()
        self.log(self.cookie_path)
        name_counter = 0
        start_time = time.time()
        self.log(f'started at {datetime.datetime.now()} with {self.user} account')
        try:
            self.log(os.linesep)
        except:
            self.log('\n')
        self.create_browser()

        self.connect_to_linkedin()
        res = self.search(self.current_keyword, self.current_page, self.browser, self.location, first=False,
                          second=False, third=False)
        if res == -1:
            self.random_wait(10, 15)
            res = self.search(self.current_keyword, self.current_page, self.browser, self.location, first=False,
                              second=False, third=False)
            if res == -1:
                raise TimeoutException('WIFI TOO SLOW FOR SEARCH')
        self.random_wait()

        while (name_counter < self.config['name_collect_amount']) and int(self.current_page) < 100:
            name_count, self.current_page = self.find_users()
            if self.current_page == -1:
                res = self.close_all_chats()
                if res == -1:
                    raise TimeoutException
                else:
                    self.browser.refresh()
                    continue
            self.log("collected " + str(name_counter) + " names")
            self.random_wait(3, 5)
            name_counter = name_counter + name_count
        error_counter = 0
        connection_counter = 0

        end_time = time.time()
        time_took = end_time - start_time
        time_took_mins = (end_time - start_time) / 60

        self.log(os.linesep)
        self.log(f'took {time_took} seconds to finish ({time_took_mins} minutes)')
        self.log(os.linesep)
        self.log(f'FINISHED AT PAGE {self.current_page}')
        self.prepare_discord_message(connection_counter, time_took_mins, self.current_page, self.current_keyword)
        self.log(os.linesep)
        self.save_cookie()
        self.browser.quit()

    def translate_names(self):
        copied_list = self.untranslated_names.copy()
        hebrew_name = ''
        for name in self.untranslated_names:
            if name not in self.translated_names.keys() and name not in self.name_blacklist:
                hebrew_name = None
                print(len(copied_list))
                print(name)
                try:
                    hebrew_name = input()
                except UnicodeDecodeError:
                    print("Error, translation problem, saved for next time")
                    continue
                if hebrew_name and hebrew_name != "ע" and hebrew_name != "ד":
                    self.translated_names[name] = hebrew_name.strip()
                    self.list_to_json(self.config_path + "translated_names.json", self.translated_names)
                elif hebrew_name == "ע":
                    self.name_blacklist.append(name)
                    self.list_to_json(self.config_path + "nameblacklist.json", self.name_blacklist)
            copied_list.remove(name)
            self.list_to_json(self.config_path + "untranslated_names.json", copied_list)
