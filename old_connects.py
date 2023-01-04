from time import sleep

from core.downloader import download_config
from core.old_connects_core import OldConnectsSearchBot

old_connects_searcher = OldConnectsSearchBot()
old_connects_searcher.main()
sleep(24400)
