import os
import time
import traceback

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import datetime

from core.base import ReturnTypes
from core.user_search_mixin import UserSearchMixin
from core.friend_request_mixin import FriendRequestMixin


class FriendRequestBot(FriendRequestMixin, UserSearchMixin):
    def __init__(self):
        super().__init__()
        self.current_page = None
        self.untranslated_names = self.json_to_list(self.config_path + "untranslated_names.json")
        self.translated_names = self.json_to_list(self.config_path + "translated_names.json")
        self.blacklist = self.json_to_list(self.config_path + "blacklist.json")
        self.name_blacklist = self.json_to_list(self.config_path + "nameblacklist.json")
        self.mandatory = self.json_to_list(self.config_path + "mandatory.json")
        self.loops = self.config['loops']
        self.actual_connects_num = 0
        self.skip_day_translate = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5,
                                   'sunday': 6}
        self.user = self.config['user']

    def do_main_task(self):
        # Check for skip day or delayed start
        user_skip_days = self.config["skip_days"]
        skip_days = [self.skip_day_translate[day.lower()] if isinstance(day, str) else day for day in user_skip_days]
        if datetime.datetime.today().weekday() in skip_days:
            self.log('Today automation was skipped.')
            return ReturnTypes.QUIT

        max_time = self.config['sleep_between_loops'] * 60
        min_time = max_time - (10 * 60)

        delayed_start = self.config.get('delayed_start')
        if delayed_start:
            self.send_to_discord(
                f'Automation triggered, will start in {min_time / 60} to {max_time / 60} minutes, user is: {self.user}')
            self.random_wait(min_time, max_time)
        self.send_to_discord(f'Automation starting now {os.linesep}{datetime.datetime.now()}')

        # Start working
        self.get_cookie_path(self.user)
        self.log(self.cookie_path)
        self.log(f'started at {datetime.datetime.now()} with {self.user} account')
        try:
            self.log(os.linesep)
        except:
            self.log('\n')
        if not self.browser:
            self.create_browser()

        self.connect_to_linkedin()

        counter = 0
        self.current_keyword = self.setup_for_run()
        saved_current_page = self.get_saved_current_page_by_keyword()
        if saved_current_page:
            self.current_page = saved_current_page
        else:
            self.current_page = 0

        start_time = time.time()
        for iterations in range(0, int(self.loops)):
            if self.config["mandatory_first_word"]:
                self.set_mandatory(self.current_keyword.split()[0])

            counter += 1
            self.log(f'Loop number {counter}', discord=True)
            self.log('#######')
            self.log(f'using keyword {self.current_keyword}')
            self.log('#######')
            new_last_page = self.main()
            if new_last_page == ReturnTypes.QUIT:
                self.log("got -2 quitting")
                self.send_error_report()
                return ReturnTypes.QUIT
            elif new_last_page == ReturnTypes.QUIT:
                self.log('Maximum connections reached, quitting')
                self.send_to_discord('Maximum connections reached. run finished.')

            if new_last_page:
                self.current_page = int(new_last_page)
                self.save_current_page(self.current_page)

            if not self.one_keyword:
                self.current_keyword = self.choose_new_keyword(old_keyword=self.current_keyword)

            self.log(f"finished loop number {counter}")
            if int(self.loops) != counter:
                self.log(f"Sleeping between loops ({int(self.config['sleep_between_loops'])} mins)")
                time.sleep(int(self.config['sleep_between_loops']) * 60)

        self.log(f'ran {counter} times!')
        self.log("*" * 50)
        self.log("END")
        self.log("*" * 50)

    def main(self):
        user_list = []
        start_time = time.time()
        res = self.search(self.current_keyword, self.current_page, self.browser, self.location)
        if res == -1:
            self.random_wait(10, 15)
            res = self.search(self.current_keyword, self.current_page, self.browser, self.location)
            if res == -1:
                raise TimeoutException('WIFI TOO SLOW FOR SEARCH')
        self.random_wait()
        while (len(user_list) < self.config['connect_amount']) and int(self.current_page) < 100:
            new_user_list, self.current_page = self.find_users()
            self.current_page = int(self.current_page)
            if self.current_page == -1:
                res = self.close_all_chats()
                if res == -1:
                    raise TimeoutException
                else:
                    self.browser.refresh()
                    continue
            user_list = user_list + new_user_list
            self.log("collected " + str(len(user_list)) + " users")
            self.random_wait(3, 5)
        error_counter = 0
        toast_error_counter = 0
        connection_counter = 0
        for link in user_list:
            res = self.friend_request(link)
            self.random_wait(3, 6)
            if res == -2:
                error_counter += 1
                if error_counter >= 3:
                    self.log('3 errors, quitting', error=self.get_error())
                    return ReturnTypes.QUIT
            elif res == ReturnTypes.ERROR:
                error_counter += 1
                if error_counter >= 3:
                    self.log('3 errors, quitting', error=self.get_error())
                    return ReturnTypes.QUIT
            elif res == ReturnTypes.TOAST_BAN:
                toast_error_counter += 1
                if toast_error_counter >= 6:
                    self.log(f"{toast_error_counter} toast errors, quitting")
                    return ReturnTypes.QUIT
            elif res == 1:
                connection_counter += 1
                self.actual_connects_num = int(self.json_to_list(self.config_path + 'actual_connects.json')['num'])
                self.actual_connects_num = self.actual_connects_num + 1
                self.save_actual_connects()
                if self.actual_connects_num >= self.config['maximum_daily_connects']:
                    self.log("QUITTING: maximum daily connects reached")
                    self.loop_end(start_time, connection_counter)
                    return ReturnTypes.MAXIMUM_CONNECTIONS
                self.log(f'connected with {connection_counter} people so far')
                self.log(f'running for {(time.time() - start_time) / 60} minutes')

        self.loop_end(start_time, connection_counter)
        return self.current_page

    def loop_end(self, start_time, connection_counter):
        end_time = time.time()
        time_took = end_time - start_time
        time_took_mins = (end_time - start_time) / 60
        self.log(f'connected with {connection_counter} people')
        self.log(os.linesep)
        self.log(f'took {time_took} seconds to finish ({time_took_mins} minutes)')
        self.log(os.linesep)
        self.log(f'FINISHED AT PAGE {self.current_page}')
        self.prepare_discord_message(connection_counter, time_took_mins, self.current_page, self.current_keyword)
        self.log(os.linesep)
        self.save_cookie()
    def save_current_page(self, current_page):
        if self.user not in self.current_page_dict:
            self.current_page_dict[self.user] = {self.current_keyword: self.current_page}
        else:
            self.current_page_dict[self.user][self.current_keyword] = current_page
        self.list_to_json(self.config_path + "current_page.json", self.current_page_dict)

    def get_saved_current_page(self):
        self.current_page_dict = self.json_to_list(self.config_path + "current_page.json")
        return self.current_page_dict

    def get_saved_current_page_by_keyword(self):
        self.get_saved_current_page()
        if self.user in self.current_page_dict.keys():
            if self.current_keyword in self.current_page_dict[self.user]:
                return self.current_page_dict[self.user][self.current_keyword]
        return None

    def find_users(self):
        exact_match = self.config['exact_match']
        self.close_all_chats()
        user_list = []

        results = self.browser.find_elements(By.XPATH, "//div[@data-view-name='search-entity-result-universal-template']")
        self.log(f"{len(results)} results found")
        print(len(results), "results found")
        for user in results:
            try:
                connect_button = user.find_element(By.XPATH, ".//button[contains(., 'Connect')]")
            except:
                print("connect button is not found")
                continue
            else:
                res = 1
                try:
                    subtitle = user.find_element(By.XPATH,
                                                 ".//div[contains(@class, 't-14 t-black t-normal')]").text

                except:
                    subtitle = ""
                    self.log("couldn't get subtitle")
                try:
                    name_title = self.get_name_title(user)

                except Exception as e:
                    self.log('Cant get name', error=self.get_error())
                    continue
                first_name = name_title.lower().split()[0]
                if first_name not in self.translated_names.keys():
                    self.log('Name not translated')
                    if first_name not in self.untranslated_names and first_name not in self.name_blacklist:
                        self.untranslated_names.append(first_name)
                        self.list_to_json(self.config_path + "untranslated_names.json", self.untranslated_names)
                    if self.config["send_connect_message"]:
                        continue

                try:
                    past_experience = user.find_element(By.XPATH,
                                                        ".//p[contains(@class, 'entity-result__summary')]").text
                except Exception as e:
                    past_experience = ""
                    self.log("couldnt get past experience", error=self.get_error(), printed=False)
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
                if not exact_match:
                    if self.mandatory:
                        for word in self.mandatory:
                            if word.lower() in subtitle.lower() or word.lower() in past_experience.lower():
                                res = 1
                                break
                        if res == -1:
                            self.log(
                                f"MANDATORY: skipping {name_title} because title doesnt have any of the mandatory words")
                            continue
                else:
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

                link = self.get_profile_link(user)
                if link not in user_list:
                    user_list.append(link)

        self.close_all_chats()
        try:
            next_button = self.get_next_button()
            next_clickable = next_button.is_enabled()
        except:
            time.sleep(30)
            return (-1, -1)
        try:
            self.close_all_chats()
            if next_clickable:
                next_button.click()
        except:
            time.sleep(30)
            return (-1, -1)
        self.random_wait(2, 4)
        self.close_all_chats()
        url = self.browser.current_url
        self.log(f'next clickable: {next_clickable}')
        if next_clickable:
            current_page = str(url.split('page=')[1].split('&')[0])
            self.log("the current page is " + current_page)
        else:
            current_page = str(100)
            self.log("REACHED LAST PAGE, ENDING")

        return user_list, current_page

    def friend_request(self, user_link):
        self.browser.get(user_link)
        minimum_experience = self.config['minimum_experience']
        maximum_experience = self.config.get('maximum_experience')
        self.close_all_chats()
        name_title = self.browser.find_element(By.XPATH, "//h1[contains(@class, 'inline t-24 v-align-middle break-word')]")
        try:
            experience_time = self.get_experience(self.current_keyword, name_title)
            if minimum_experience:
                if experience_time < int(minimum_experience):
                    self.log(
                        f'MINIMUM EXPERIENCE: skipping {name_title.text} because experience ({experience_time} years) is less than'
                        f' {minimum_experience} years')
                    return 0
            if maximum_experience:
                if experience_time > int(maximum_experience):
                    self.log(
                        f'MAXIMUM EXPERIENCE: skipping {name_title.text} because experience ({experience_time} years) is more than'
                        f' {maximum_experience} years')
                    return 0
        except Exception as e:
            print(traceback.format_exc())
            self.log('failed to get experience')
            if self.config["minimum_experience"] > 0:
                self.log('skipping')
                return 0

        first_name = name_title.text.lower().split()[0]
        connect_button = self.get_connect_button(name_title.text)

        if not connect_button:
            self.log("Problem with connect button")
            return
        else:
            subtitle = ""
            try:
                subtitle = self.browser.find_element(By.XPATH,
                                                     "//div[contains(@class, 't-14 t-black t-normal')]")
            except:
                pass

            self.random_wait(5, 7)
            self.click_connect_button(connect_button)
            block_check = self.chain_block_check(name_title.text)
            if block_check:
                return block_check
            email_block = self.check_for_email_prompt()
            if email_block:
                self.log("EMAIL BLOCK: can't connect because user has defined email block")
                return 0
            self.random_wait(5, 7)
        if self.config['send_connect_message']:
            try:
                res = self.send_connect_request_with_message(self.translated_names, first_name, name_title.text,
                                                             subtitle.text)
                if res == ReturnTypes.CONTINUE:
                    return ReturnTypes.CONTINUE
                self.random_wait()
                ban_block_check = self.chain_block_check(name_title.text)
                if ban_block_check != 0:
                    return ban_block_check

                self.log(f'{name_title.text}, {subtitle} connected')
                return 1

            except Exception as e:
                self.log('unable to send friend request', error=self.get_error())
                self.save_error_screenshot("UNABLE_ERROR")

                self.log(user_link, error=self.ge)
                self.random_wait()
                return -1

        else:
            try:
                self.send_connect_request_no_message()

            except Exception as e:
                self.log('unable to send friend request', error=self.get_error())
                self.save_error_screenshot("UNABLE_ERROR")
                self.log(user_link, error=e)
                self.random_wait()
                return -1



            self.log(f'{name_title.text}, {subtitle} connected')
            return 1

    def save_actual_connects(self, num=None):
        if num:
            self.list_to_json(self.config_path + "actual_connects.json", {"num": num})
        else:
            self.list_to_json(self.config_path + "actual_connects.json", {"num": self.actual_connects_num})

    def load_actual_connects(self):
        self.actual_connects_num = self.json_to_list(self.config_path + "actual_connects.json").get("num")
        return self.actual_connects_num
