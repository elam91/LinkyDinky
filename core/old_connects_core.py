import os
from datetime import datetime, date
import time

from selenium.common.exceptions import TimeoutException

from core.friend_request_core import FriendRequestBot
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class OldConnectsSearchBot(FriendRequestBot):
    def __init__(self, start_page=0):
        super().__init__()
        self.old_names = []
        self.current_page = start_page
        self.loops = self.config.get('old_connects_loops', 1)
        self.username = ''

    def find_users(self):
        exact_match = self.config['exact_match']
        self.close_all_chats()
        user_list = []
        results = self.browser.find_elements(By.XPATH, "//div[@class='entity-result__item']")
        for user in results:
            print("*" * 10)
            try:
                message_button = user.find_element(By.XPATH, ".//span[text()='Message']")
            except:
                continue
            else:
                res = 1
                try:
                    subtitle = user.find_element(By.XPATH,
                                                 ".//div[@class='entity-result__primary-subtitle t-14 t-black t-normal']").text

                except:
                    subtitle = ""
                    continue
                try:
                    name_title = self.get_name_title(user)
                except:
                    name_title = ""
                if name_title:
                    first_name = name_title.lower().split()[0]
                    if first_name not in self.translated_names.keys():
                        if first_name not in self.untranslated_names and first_name not in self.name_blacklist and first_name not in self.translated_names.keys():
                            self.untranslated_names.append(first_name)
                            self.list_to_json(self.config_path + "untranslated_names.json", self.untranslated_names)
                else:
                    self.log("cant get name")
                if name_title in self.old_names:
                    continue
                else:
                    self.old_names.append(name_title)
                try:
                    past_experience = user.find_element(By.XPATH,
                                                        ".//p[contains(@class, 'entity-result__summary')]").text
                except Exception as e:
                    past_experience = ""
                whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

                for word in name_title.lower().split():
                    if word in self.name_blacklist:
                        self.log(f"NAME BLACKLIST: {name_title} blacklisted name {word}, skipping")
                        res = -1
                        break
                if res == -1:
                    continue
                filtered_subtitle = ''.join(filter(whitelist.__contains__, subtitle))

                for word in self.blacklist:
                    if word.lower() in filtered_subtitle.lower().split():
                        self.log(f"BLACKLIST: skipping {name_title} because title has the word {word}")
                        res = -1
                        break
                if res == -1:
                    continue
                res = -1

                if exact_match:
                    res1 = 1
                    res2 = 1
                    for word in self.current_keyword.lower().split():
                        if word not in filtered_subtitle.lower():
                            res1 = -1
                            break
                    if past_experience:
                        if "current:" not in past_experience:
                            res2 = -1
                        else:
                            for word in self.current_keyword.lower().split():
                                if word not in past_experience.lower():
                                    res2 = -1
                                    break
                    if res1 == -1 and res2 == -1:
                        self.log(
                            f'EXACT MATCH: skipping {name_title} because {filtered_subtitle} does not contain {self.current_keyword.lower()}')
                        continue
                print("before close chats")
                self.close_all_chats()
                self.random_wait(1, 2)
                print("after close chats, before trying to click message button")
                message_button.click()
                print('after clicking message button')
                element_present = EC.presence_of_element_located((By.XPATH,
                                                                  ".//button[contains(@class, 'msg-overlay-bubble-header__control')]//li-icon[contains(@type,'maximize')]/.."))
                expand_button = WebDriverWait(self.browser, 10).until(element_present)
                print('before click expand button')
                self.click_button_humanly(expand_button)
                print('after expand')
                time.sleep(1)
                element_present = EC.presence_of_element_located(
                    (By.XPATH, "//ul[contains(@class, 'msg-s-message-list-content')]"))
                try:
                    message_list = WebDriverWait(self.browser, 10).until(element_present)
                except:
                    link = user.find_element(By.XPATH, ".//a[contains(@class, 'app-aware-link')]")
                    if link.get_attribute('href') not in user_list:
                        user_list.append(link.get_attribute('href'))
                    continue
                valid = True
                needed_time_delta = 30 * self.config["old_connect_month_delta_unanswered"]
                messages = message_list.find_elements(By.XPATH, "//li[contains(@class, 'msg-s-message-list__event')]")
                print(len(messages), name_title)
                if len(messages) == 0:
                    continue
                if len(messages) > 2:
                    continue
                for message in messages:
                    try:
                        sender = message.find_element(By.CLASS_NAME,
                                                      'msg-s-event-listitem__profile-picture').get_attribute(
                            'title')
                        print(sender)
                    except:
                        continue
                    if sender != self.username:
                        needed_time_delta = 30 * self.config["old_connect_month_delta_answered"]
                if valid == False:
                    print("found diff sender")
                    continue
                else:
                    print("only user is sender")

                message_time = message_list.find_elements(By.XPATH,
                                                          ".//time[contains(@class, 'msg-s-message-list__time-heading')]")[
                    -1].text
                message_time_split = message_time.split()
                today = datetime.today()
                if len(message_time_split) == 1:  # just a day, means its recent, pass
                    print("just day, too recent, continue")
                    continue
                elif len(message_time_split) == 2:  # just month without year, in this last year
                    new_message_time = message_time + ", " + str(date.today().year)
                    date_object = datetime.strptime(new_message_time.lower().capitalize(), "%b %d, %Y")
                    print(date_object)
                    time_delta = (today - date_object).days
                    print('time delta is ' + str(time_delta) + " days")
                    if time_delta < needed_time_delta:
                        valid = False
                elif len(message_time_split) == 3:  # from a previous year
                    date_object = datetime.strptime(message_time.lower().capitalize(), "%b %d, %Y")
                    print(date_object)
                    time_delta = (today - date_object).days
                    print('time delta is ' + str(time_delta) + " days")
                    if time_delta < needed_time_delta:
                        valid = False
                else:
                    continue
                print('valid', valid)

                self.close_all_chats()
                if valid:
                    link = self.get_profile_link(user)
                    if link not in user_list:
                        user_list.append(link)
                self.close_all_chats()
            self.list_to_json(self.config_path + 'old_names.json', self.old_names)
            self.random_wait(1, 2)

        self.close_all_chats()
        self.random_wait()
        next_button = self.get_next_button()
        if not next_button.is_enabled():
            self.current_page = 100
            self.log("REACHED LAST PAGE, ENDING")
            return user_list, self.current_page
        try:
            self.close_all_chats()
            next_button.click()
        except:
            time.sleep(30)
            return (-1, -1)
        self.random_wait(2, 4)
        self.close_all_chats()
        url = self.browser.current_url
        self.current_page = str(url.split('page=')[1].split('&')[0])
        self.log("the current page is " + self.current_page)
        return user_list, int(self.current_page)

    def get_username(self):
        user_photo = self.browser.find_element(By.XPATH, ".//img[contains(@class, 'global-nav__me-photo')]")
        self.username = user_photo.get_attribute('alt')
        self.log(f'username is {self.username}')

    def main(self):
        self.setup_for_run()
        for iterations in range(0, int(self.loops)):
            res = self.main_loop()
            if res == -2:
                return

    def main_loop(self):
        old_connects = []
        config = self.config
        self.list_to_json(self.config_path + 'old_connects.json', old_connects)
        self.log(self.cookie_path)
        start_time = time.time()
        self.log(f'started at {datetime.now()} with {self.user} account')
        try:
            self.log(os.linesep)
        except:
            self.log('\n')

        self.create_browser()

        user_list = []
        self.connect_to_linkedin()
        self.get_username()
        res = self.search(self.current_keyword, self.current_page, self.browser, self.location, first=True,
                          second=False, third=False)

        if res == -1:
            self.random_wait(10, 15)
            res = self.search(self.current_keyword, self.current_page, self.browser, self.location, first=True,
                              second=False, third=False)
            if res == -1:
                raise TimeoutException('WIFI TOO SLOW FOR SEARCH')
        self.random_wait()

        while self.current_page is not None and self.current_page != 100 and len(user_list) < config['resend_amount']:
            new_user_list, self.current_page = self.find_users()
            user_list = user_list + new_user_list
            self.log("collected " + str(len(user_list)) + " users")
            self.random_wait(3, 5)
            if self.current_page == 100:
                break

        for link in user_list:
            self.browser.execute_script(f'''window.open("{link}","_blank");''')
        if self.current_page == 100:
            return -2
