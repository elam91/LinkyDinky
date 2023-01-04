from core.base import BaseLinkedinBot
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime


class FriendRequestMixin(BaseLinkedinBot):
    def __init__(self):
        super().__init__()

    def connect_to_linkedin(self):
        if not self.browser:
            self.create_browser()
        self.browser.get('https://www.linkedin.com/')
        print('loading cookie')
        self.load_cookie()
        print('sleeping')
        self.random_wait()
        print('refreshing')
        self.browser.refresh()
        try:
            self.browser.maximize_window()
        except Exception as e:
            self.log("Couldn't maximize window", error=str(e))

    def get_experience(self, keyword, name_title):
        self.random_wait(2, 3)

        element_present = EC.presence_of_element_located(
            (By.XPATH, "//div[@id='experience']/.."))
        experience_list = WebDriverWait(self.browser, 5).until(element_present)
        experience_items = experience_list.find_elements(By.CSS_SELECTOR, 'li.artdeco-list__item')
        years = 0
        months = 0

        current_job = experience_items[0]
        for item in experience_items:
            try:
                roles = item.find_elements(By.CSS_SELECTOR, 'span.t-bold')
                roles = [role.find_element(By.CSS_SELECTOR,
                                           'span.visually-hidden').text.lower() for role in roles]
            except:
                continue
            if len(roles) == 1:
                multiple_roles = False
                role = roles[0]
            else:
                multiple_roles = True

            if item == current_job:
                blacklist_company = self.check_employer_blacklist(item, name_title.text)
                if blacklist_company:
                    self.log(
                        f'EMPLOYER BLACKLIST: skipping {name_title.text} because banned employer {blacklist_company.upper()} was found')
                    return 0

            if not multiple_roles:
                res = self.get_experience_for_single_role(item, keyword, role, name_title.text)
                years = years + res['years']
                months = months + res['months']
            if multiple_roles:
                subitems = item.find_elements(By.TAG_NAME, 'li')
                for subitem in subitems:
                    try:
                        sub_role = subitem.find_element(By.CSS_SELECTOR, 'span.t-bold').find_element(By.CSS_SELECTOR,
                                                                                                     'span.visually-hidden').text
                    except:
                        continue
                    res = self.get_experience_for_single_role(subitem, keyword, sub_role, name_title.text)
                    years = years + res['years']
                    months = months + res['months']

        experience_time = (datetime.timedelta(days=((months * 30) + (years * 365))) / datetime.timedelta(
            days=1)) / 365
        self.log(f"Experience is {experience_time}")
        return experience_time

    def check_for_toast_ban(self, name):
        banned = False
        try:
            element_present = EC.presence_of_element_located(
                (By.XPATH,
                 "//p[contains(@class, 'artdeco-toast-item__message')]//span[contains(., 'Unable to connect')]/.."))
            send_button = WebDriverWait(self.browser, 5).until(element_present)
        except:
            pass
        else:
            banned = True
            message = f"""
            PROBABLY TEMP BANNED - TOAST KIND, seen ban popup when trying to connect with {name}
            """
            self.log(message, error=1)
            self.save_error_screenshot("TEMPORARY_BAN")
        return banned

    def check_for_connection_limit_ban(self, name):
        banned = False
        try:
            element_present = EC.presence_of_element_located(
                (By.XPATH, "//button[contains(@class, 'artdeco-button')]//*[contains(., 'Got it')]/.."))
            send_button = WebDriverWait(self.browser, 5).until(element_present)
        except:
            pass
        else:
            banned = True
            message = f"""
                        PROBABLY TEMP BANNED, seen ban popup when trying to connect with {name}
                        """
            self.log(message, error=1)
            self.send_error_report()
            self.save_error_screenshot("TEMPORARY_BAN")
        return banned

    def get_connect_button(self, name):
        try:
            element_present = EC.presence_of_element_located(
                (By.XPATH,
                 f".//button[@aria-label='Invite {name} to connect']"))
            connect_button = WebDriverWait(self.browser, 10).until(element_present)
            connect_buttons = self.browser.find_elements(By.XPATH, f".//button[@aria-label='Invite {name} to connect']")
            print(f"LEN OF CONNECT_BUTTONS: {len(connect_buttons)}")
            connect_button = connect_buttons[-1]
        except:
            return False
        return connect_button

    def click_connect_button(self, button):
        self.click_button_humanly(button)

    def send_connect_request_no_message(self):
        try:
            send_button = self.get_generic_linkedin_button('Send')
            self.random_wait(7, 8)
            self.click_button_humanly(send_button)
            self.random_wait()
        except:
            try:
                send_button = self.get_generic_linkedin_button('No')
                self.random_wait(1, 3)
                self.click_button_humanly(send_button)
                self.random_wait()
            except:
                try:
                    self.handle_where_do_you_know_from()
                    send_button = self.get_generic_linkedin_button('Send')
                    self.click_button_humanly(send_button)
                    self.random_wait(2, 3)
                except Exception as e:
                    raise e

    def send_connect_request_with_message(self, translated_names, first_name, full_name, subtitle):
        message = self.json_to_list(self.config_path + "messages.json")['connect_message']

        if first_name in translated_names.keys():
            try:
                message = message.replace('{name}', translated_names[first_name])

                note_button = self.get_generic_linkedin_button('Add a note')
                self.click_button_humanly(note_button)
                self.random_wait()
            except:
                try:
                    self.handle_where_do_you_know_from()
                    self.random_wait(1, 3)
                    note_button = self.get_generic_linkedin_button('Add a note')

                    self.click_button_humanly(note_button)
                    self.random_wait()
                except:
                    self.log('cant do where button')
                    return 0
            element_present = EC.presence_of_element_located((By.ID, "custom-message"))
            text_box = WebDriverWait(self.browser, 5).until(element_present)
            text_box.send_keys(message)
            self.random_wait(1, 2)

            element_present = EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[@aria-label='Send now' and @class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1']//span[text()='Send']"))

            send_button = WebDriverWait(self.browser, 5).until(element_present)
            send_button_clickable = send_button.is_enabled()
            self.log(full_name, "clickable", send_button_clickable)
            if send_button_clickable:
                print('clicking')
                self.click_button_humanly(send_button)
                print('after click')
                return 1

    def handle_where_do_you_know_from(self):
        self.log('reached how do you know button')
        where_button = self.browser.find_element(By.XPATH,
                                                 "//button[@role='radio' and @aria-label='Other']")
        self.log('got where button')
        self.click_button_humanly(where_button)
        self.log('button clicked')
        connect_button = self.get_generic_linkedin_button('Connect')
        self.click_button_humanly(connect_button)

    def check_for_email_prompt(self):
        email = False
        try:
            email_input = self.browser.find_element(By.NAME, 'email')
            if email_input:
                email = True
        except:
            pass
        return email

    def check_employer_blacklist(self, item, full_name):
        current_work_blacklist = self.json_to_list(self.config_path + "currentworkblacklist.json")
        for company in current_work_blacklist['employer']:
            if company in item.text.lower():
                return company
            else:
                return False

    def check_position_blacklist(self, role, full_name):
        current_work_blacklist = self.json_to_list(self.config_path + "currentworkblacklist.json")
        for phrase in current_work_blacklist['position']:
            if phrase in role.lower().split():
                return phrase
            else:
                return False

    def get_experience_for_single_role(self, item, keyword, role, full_name):
        years = 0
        months = 0
        blacklist_phrase = self.check_position_blacklist(role, full_name)
        if blacklist_phrase:
            self.log(
                f'POSITION BLACKLIST: skipping {full_name} because banned position phrase {blacklist_phrase.upper()} was found')
            return {"years": years, "months": months}
        experience = None
        if keyword.split()[-1].lower().strip() in role.lower().split() or 'developer' in role.lower().split() \
                or 'engineer' in role.lower().split() or 'architect' in role.lower().split():
            try:
                unfiltered_list = item.find_elements(By.CSS_SELECTOR, 'span.t-black--light')
            except:
                return {"years": years, "months": months}
            for element in unfiltered_list:
                if 'mo' in element.text or 'yr' in element.text:
                    experience = element
                    break
            try:
                experience = experience.find_element(By.CSS_SELECTOR, 'span.visually-hidden').text
            except:
                return {"years": years, "months": months}
            if 'sr' in role or 'senior' in role:
                years = years + 4
            experience = experience.split('·')[1].strip().split()

            for index, word in enumerate(experience):
                if 'yr' in word:
                    years = years + int(experience[index - 1])
                if 'mo' in word:
                    months = months + int(experience[index - 1])

        return {"years": years, "months": months}
