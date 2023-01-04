import requests

from core.downloader import download_config, download_keywords
from core.friend_request_core import FriendRequestBot


friend_requester = FriendRequestBot()
friend_requester.save_actual_connects(0)
try:
    while friend_requester.load_actual_connects() < friend_requester.config.get('minimum_daily_connects'):
        res = friend_requester.do_main_task()
        if res == -2:
            break
    friend_requester.browser.quit()
except Exception as error:
    friend_requester.log("Exception while running friend requests", error=error)
    friend_requester.send_error_report()
    raise error
