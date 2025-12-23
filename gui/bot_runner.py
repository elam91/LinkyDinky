import threading
import sys
import os
import io

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

class OutputCapture:
    def __init__(self, callback):
        self.callback = callback
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        if text.strip():
            self.callback(text.strip())
        self.original_stdout.write(text)
        
    def flush(self):
        self.original_stdout.flush()

class BotRunner:
    def __init__(self, on_log_callback, on_status_change=None):
        self.thread = None
        self.running = False
        self.on_log = on_log_callback
        self.on_status_change = on_status_change
        self.stop_requested = False
        
    def start(self, script="request_minimum", keyword=None):
        if self.running:
            self.on_log("Bot is already running!")
            return
        
        self.running = True
        self.stop_requested = False
        if self.on_status_change:
            self.on_status_change("running")
        
        self.thread = threading.Thread(target=self._run_bot, args=(script, keyword), daemon=True)
        self.thread.start()
    
    def stop(self):
        if not self.running:
            self.on_log("Bot is not running!")
            return
        
        self.stop_requested = True
        self.on_log("Stop requested - bot will stop after current operation...")
        
        if self.on_status_change:
            self.on_status_change("stopping")
    
    def _run_bot(self, script, keyword):
        capture = OutputCapture(self.on_log)
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = capture
            sys.stderr = capture
            
            self.on_log(f"Starting {script}...")
            
            if keyword:
                sys.argv = ['', '--keyword'] + keyword.split()
                self.on_log(f"Using keyword: {keyword}")
            else:
                sys.argv = ['']
            
            if script == "request_minimum":
                self._run_request_minimum()
            elif script == "withdraw_requests":
                self._run_withdraw_requests()
            elif script == "request_loops":
                self._run_request_loops()
            elif script == "old_connects":
                self._run_old_connects()
            elif script == "search_first_names":
                self._run_search_first_names()
            elif script == "scheduler":
                self._run_scheduler()
            elif script == "unmessaged_connects":
                self._run_unmessaged_connects()
            else:
                self.on_log(f"Unknown script: {script}")
            
            self.on_log("Bot completed!")
            
        except Exception as e:
            self.on_log(f"Error running bot: {str(e)}")
            import traceback
            self.on_log(traceback.format_exc())
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            self.running = False
            self.stop_requested = False
            if self.on_status_change:
                self.on_status_change("idle")
    
    def _run_request_minimum(self):
        from core.base import ReturnTypes
        from core.friend_request_core import FriendRequestBot
        
        friend_requester = FriendRequestBot()
        friend_requester.save_actual_connects(0)
        try:
            while friend_requester.load_actual_connects() < friend_requester.config.get('minimum_daily_connects'):
                if self.stop_requested:
                    self.on_log("Stop requested, exiting...")
                    break
                res = friend_requester.do_main_task()
                if res == ReturnTypes.QUIT or res == ReturnTypes.MAXIMUM_CONNECTIONS:
                    break
            if friend_requester.browser:
                friend_requester.browser.quit()
        except Exception as error:
            friend_requester.log("Exception while running friend requests", error=error)
            raise error
    
    def _run_withdraw_requests(self):
        from core.withdraw_core import WithdrawBot
        
        request_withdraw = WithdrawBot()
        request_withdraw.main()
    
    def _run_request_loops(self):
        from core.base import ReturnTypes
        from core.friend_request_core import FriendRequestBot
        import json
        
        with open(os.path.join(BASE_DIR, "config/config.json"), "r") as f:
            config = json.load(f)
        
        loops = config.get('loops', 3)
        for i in range(loops):
            if self.stop_requested:
                self.on_log("Stop requested, exiting...")
                break
            self.on_log(f"Starting loop {i + 1} of {loops}")
            friend_requester = FriendRequestBot()
            friend_requester.save_actual_connects(0)
            try:
                while friend_requester.load_actual_connects() < friend_requester.config.get('minimum_daily_connects'):
                    if self.stop_requested:
                        break
                    res = friend_requester.do_main_task()
                    if res == ReturnTypes.QUIT or res == ReturnTypes.MAXIMUM_CONNECTIONS:
                        break
                if friend_requester.browser:
                    friend_requester.browser.quit()
            except Exception as error:
                friend_requester.log("Exception while running friend requests", error=error)
                raise error
    
    def _run_old_connects(self):
        from core.old_connects_core import OldConnectsSearchBot
        
        old_connects_searcher = OldConnectsSearchBot()
        old_connects_searcher.main()
    
    def _run_search_first_names(self):
        from core.name_translate_core import NameCollectorBot
        
        name_collector = NameCollectorBot()
        name_collector.main()
    
    def _run_scheduler(self):
        self.on_log("Scheduler is not supported in GUI mode - use the command line instead")
    
    def _run_unmessaged_connects(self):
        from core.unmessaged_connects_core import UnmessagedConnectsBot
        
        unmessaged_connects_searcher = UnmessagedConnectsBot()
        unmessaged_connects_searcher.main()
