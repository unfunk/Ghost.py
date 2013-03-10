import logging
import gc
from ghost import Ghost, BlackPearl
from GhostWork import GhostWork

gc.set_debug(gc.DEBUG_LEAK)


logger = logging.getLogger('backpearl')
logger.setLevel(logging.DEBUG)

gh = Ghost(display=True,
            cache_size=10000,
            wait_timeout=30,
            prevent_download=["jpg", "png", "gif"],
            download_images=False,
            individual_cookies=True)

blackPerl = BlackPearl(gh, GhostWork)
blackPerl.start()
