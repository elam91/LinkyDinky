import time

import schedule

from core.friend_request_core import FriendRequestBot

friend_requester = FriendRequestBot()

SCHEDULE_TIME = friend_requester.config['scheduled_time']

friend_requester.log(f'Scheduled at {SCHEDULE_TIME}')
try:
    schedule.every().day.at(SCHEDULE_TIME).do(friend_requester.do_main_task)
except Exception as error:
    friend_requester.log("Exception while running SCHEDULED friend requests", error=friend_requester.get_error())
    friend_requester.send_error_report()
    raise error

while True:
    schedule.run_pending()
    time.sleep(1)
