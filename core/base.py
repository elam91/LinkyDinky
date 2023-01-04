import argparse
import os
import sys
import time
from collections import deque

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
import json
import random
import discord
from discord import Webhook, RequestsWebhookAdapter, Embed
import datetime
from pathlib import Path

_ALLOWED_ARGUMENTS = ['user', 'start_page', 'loops', 'connect_amount',
                      'minimum_experience', 'location', 'sleep_between_loops',
                      'name_connect_amount', 'minimum_daily_connects', 'maximum_daily_connects',
                      'resend_amount', 'webhook_url', 'chromedriver_path']

_ALLOWED_BOOL_ARGUMENTS = ['exact_match', 'send_connect_message', 'delayed_start', 'mandatory_first_word']


class BaseLinkedinBot:
    def __init__(self):
        self._parser = argparse.ArgumentParser(
            prog='LinkyDinky',
            description='LinkedIn Recruiter Automator',
            epilog='')
        self.custom_keyword = None
        self._add_parse_arguments()
        self.last_log = ''
        self.browser = None
        self.config_path = "config/"
        self.current_keyword = None
        self.config = self.json_to_list(self.config_path + 'config.json')
        self._apply_bash_args()
        self.user = self.config['user']
        self.keywords_keep = self.json_to_list(self.config_path + 'keywordskeep.json')
        self.keywords = self.json_to_list(self.config_path + 'keywords.json')
        self.current_page_dict = self.json_to_list(self.config_path + 'current_page.json')
        self.location = self.config.get('location', 'Israel')
        self.get_cookie_path(self.user)
        self.one_keyword = False

        if self.user not in self.current_page_dict.keys():
            self.current_page_dict[self.user] = {}

    def _add_parse_arguments(self):
        for argument in _ALLOWED_ARGUMENTS:
            self._parser.add_argument(f'--{argument}')
        for argument in _ALLOWED_BOOL_ARGUMENTS:
            self._parser.add_argument(f'--{argument}', action='store_true')
        self._parser.add_argument('--keyword', nargs='+')

    def _apply_bash_args(self):
        args = self._parser.parse_args()
        for attr, value in args.__dict__.items():
            if attr == '--keyword':
                self.custom_keyword = ' '.join(value)
            else:
                if value is not None:
                    self.config[attr] = value




    def get_generic_linkedin_button(self, button_text):
        element_present = EC.presence_of_element_located(
            (By.XPATH, f"//button[contains(@class, 'artdeco-button')]//*[contains(., '{button_text}')]/.."))
        button = WebDriverWait(self.browser, 5).until(element_present)
        return button

    def random_wait(self, min_num=8, max_num=13):
        random_number = random.uniform(min_num, max_num)
        print(f'sleeping for {round(random_number, 0)} seconds')
        time.sleep(random_number)

    def get_cookie_path(self, username):
        self.cookie_path = f"cookies/{username}cookie.json"
        return self.cookie_path

    @classmethod
    def json_to_list(self, path):
        with open(path, 'r') as f:
            new_str = json.load(f)
            return new_str

    @classmethod
    def list_to_json(self, path, list):
        with open(path, 'w', encoding="UTF-8") as f:
            json.dump(list, f, ensure_ascii=False, indent=4)

    def log(self, message, error=None, printed=True, discord=False):
        path = f"./logs/{datetime.datetime.today().year}/{datetime.datetime.today().month}"
        file_name = f"log_{datetime.date.today()}.txt"
        error_file_name = f"log_{datetime.date.today()}.txt"
        self.last_log = message
        try:
            if printed:
                print(message)
            Path(path).mkdir(parents=True, exist_ok=True)
            with open(os.path.join(path, file_name), "a") as f:
                f.write(message)
                try:
                    f.write('\n')
                except:
                    f.write(os.linesep)

            if error:
                with open(os.path.join(path, error_file_name), "a") as errorf:
                    errorf.write("*!" * 50)
                    errorf.write(message)
                    errorf.write("*!" * 50)
                    errorf.write(str(error))
                    errorf.write("*!" * 50)
                    try:
                        errorf.write('\n')
                    except:
                        errorf.write(os.linesep)
            if discord:
                self.send_to_discord(message)
        except:
            pass

    def close_all_chats(self):
        try:
            print("trying to close chats that are in the way")
            close_buttons = self.browser.find_elements(By.XPATH,
                                                       "//button[contains(@class, 'msg-overlay-bubble-header__control')]//li-icon[contains(@type,'close')]/..")
            for button in close_buttons:
                button.click()
            minimize_button = self.browser.find_element(By.XPATH,
                                                        "//button[contains(@class, 'msg-overlay-bubble-header__control')]//li-icon[contains(@type,'chevron-down-icon')]/..")
            minimize_button.click()
            return 1
        except Exception as e:
            if self.last_log != "couldn't close chats":
                self.log("couldn't close chats", printed=False)
            pass

    def create_browser(self):
        chromedriver_path = self.config['chromedriver_path']
        options = webdriver.ChromeOptions()
        options.headless = False
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)
        if chromedriver_path:
            service = Service(chromedriver_path)
        else:
            service = Service()
        self.browser = webdriver.Chrome(service=service, options=options)
        stealth(self.browser, languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True, )

        return self.browser

    def set_mandatory_senior(self):
        mandatory = self.json_to_list(self.config_path + 'mandatory.json')
        if "senior" in self.current_keyword.lower():
            if 'senior' not in mandatory:
                mandatory.append('senior')
        else:
            if 'senior' in mandatory:
                while 'senior' in mandatory:
                    mandatory.remove('senior')
        self.list_to_json(self.config_path + 'mandatory.json', mandatory)

    def set_mandatory(self, phrase):
        mandatory = [phrase]
        self.list_to_json(self.config_path + 'mandatory.json', mandatory)

    def choose_new_keyword(self, old_keyword):
        if self.custom_keyword:
            self.current_keyword = self.custom_keyword
            self.set_mandatory_senior()
            self.log(f"KEYWORD: {self.current_keyword}")
            return self.custom_keyword
        try:
            self.keywords.remove(old_keyword)
        except ValueError:
            pass
        self.list_to_json(self.config_path + "keywords.json", self.keywords)
        if not self.keywords:
            self.reset_keywords()
            self.keywords = self.json_to_list(self.config_path + "keywords.json")
        self.current_keyword = random.choice(self.keywords)
        self.set_mandatory_senior()
        self.log(f"KEYWORD: {self.current_keyword}")
        return self.current_keyword

    def reset_keywords(self):
        self.keywords = self.keywords_keep
        self.list_to_json(self.config_path + "keywords.json", self.keywords_keep)

    def save_config_variable_to_json(self):
        self.list_to_json(self.config_path + '/config.json', self.config)

    def setup_for_run(self):
        if not self.keywords:
            self.reset_keywords()

        if len(self.keywords_keep) == 1:
            self.one_keyword = True
        else:
            self.one_keyword = False
        self.save_config_variable_to_json()

        self.current_keyword = self.choose_new_keyword(self.current_keyword)
        self.set_mandatory_senior()
        return self.current_keyword

    def send_error_report(self):
        path = f"./logs/{datetime.datetime.today().year}/{datetime.datetime.today().month}/log_{datetime.date.today()}.txt"
        with open(path, "rb") as f:
            send_file = discord.File(f)
        with open(path, "r") as f:
            last_line = self.tail(f)
        embed = discord.Embed(title="An error has occurred",
                              description=datetime.datetime.now().date().strftime('%d/%m/%Y'))
        embed.add_field(name="**Last log line**", value=last_line)
        self.send_to_discord(embed=embed, file_obj=send_file)
        return

    def tail(self, file, n=5):
        'Return the last n lines of a file'
        return ''.join(deque(file, n))

    def prepare_discord_message(self, connection_num, run_time, finish_page, keyword=None,
                                title="Finished LinkedIn loop successfully!", action="Connected"):
        embed = discord.Embed(title=title,
                              description=datetime.datetime.now().date().strftime('%d/%m/%Y'))
        if keyword:
            embed.add_field(name="**Keyword**", value=keyword)
        embed.add_field(name=f"**{action} with**", value=f"{connection_num} people")
        embed.add_field(name="**Finished at page**", value=finish_page)
        embed.add_field(name="**Run time**", value=f"{run_time} minutes")
        self.send_to_discord(embed=embed)
        return

    def send_to_discord(self, message=None, embed=None, file_obj=None):
        webhook_url = self.config['webhook_url']
        if webhook_url:
            webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())
            data = dict()
            if message:
                message = "-" * 50 + "\n" + message + "\n" + "-" * 50
                webhook.send(content=message)
            if embed:
                if file_obj:
                    webhook.send(embed=embed, file=file_obj)
                else:
                    webhook.send(embed=embed)
        return

    def error_handler(self, connect_button=None):
        if connect_button:
            self.random_wait(10, 15)
            connect_button.click()
            try:
                element_present = EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(@class, 'artdeco-button')]//*[contains(., 'Send')]/.."))
                send_button = WebDriverWait(self.browser, 5).until(element_present)
                self.random_wait(7, 8)
                send_button.click()
            except:
                self.log("Error handler exception")
                return 0
            try:
                error_message = self.browser.find_element(By.XPATH,
                                                          "//p[contains(@class, 'artdeco-toast-item__message')]//span[contains(., 'Unable to connect')]/..")
            except:
                return 1
        try:
            retry_button = self.browser.find_element(By.XPATH, ".//span[text()='Retry search']")
        except:
            self.browser.refresh()
            self.log('Waiting a few minutes to see if that solves the problem')
            self.random_wait(120, 300)
            self.browser.refresh()
            return 0
        else:
            retry_button.click()
            self.random_wait()
            return 2

    def load_cookie(self):
        with open(self.cookie_path, 'r') as cookiesfile:
            cookies = json.load(cookiesfile)
        for cookie in cookies:
            if 'sameSite' in cookie:
                if cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                    cookie['sameSite'] = 'None'
            self.browser.add_cookie(cookie)

    def save_cookie(self):
        cookies_list = self.browser.get_cookies()
        with open(self.cookie_path, 'w') as cookiesfile:
            json.dump(cookies_list, cookiesfile)

    def save_error_screenshot(self, prefix):
        Path('../screenshots').mkdir(parents=True, exist_ok=True)
        self.browser.save_screenshot(f'./screenshots/{prefix}_' + str(datetime.datetime.now()) + ".png")

    def scroll_to_element(self, element):
        self.browser.execute_script("arguments[0].scrollIntoView();", element)

    def click_button_humanly(self, button):
        x, y = button.size["width"], button.size["height"]

        random_x = random.randint(0, x - 1)
        random_y = random.randint(0, y - 1)

        actions = ActionChains(self.browser)
        try:
            actions.move_to_element_with_offset(button, random_x, random_y).click(button).perform()
        except MoveTargetOutOfBoundsException:
            self.scroll_to_element(button)
            actions.move_to_element_with_offset(button, random_x, random_y).click(button).perform()

    def erase_current_page_json(self):
        self.list_to_json(self.config_path + "current_page.json", {})

    def erase_specific_keyword_saved_page(self, keyword, user):
        current_pages = self.json_to_list(self.config_path + "current_page.json")
        current_pages[user][keyword] = None
        self.list_to_json(self.config_path + "current_page.json", current_pages)
