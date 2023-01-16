from time import sleep
from core.old_connects_core import OldConnectsSearchBot

old_connects_searcher = OldConnectsSearchBot()
old_connects_searcher.create_browser()
old_connects_searcher.connect_to_linkedin()
old_connects_searcher.open_tabs_from_json()
sleep(24400)
