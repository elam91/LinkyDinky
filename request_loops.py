from core.friend_request_core import FriendRequestBot


friend_requester = FriendRequestBot()
try:
    res = friend_requester.do_main_task()

except Exception as error:
    friend_requester.log("Exception while running friend requests", error=friend_requester.get_error())
    friend_requester.send_error_report()
    raise error
