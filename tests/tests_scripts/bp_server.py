import logging
from ghost import Ghost, BlackPearl, Pirate

logger = logging.getLogger('backpearl')
logger.setLevel(logging.DEBUG)

class GhostWork(Pirate):
    # Every pirate instance will have a self.page (Ghost Tab) living.
    
    def _add_events(self):
        def ev_open_page():
            p = self.page.open("http://news.ycombinator.com/",
                wait_onload_event=True, wait_for_loading=False)
            
            # Every event has to return a tuple with (boolean, result_data)
            # boolean indicated if the event has run successfully. If not the event will
            # be executed until the it's return True. 
            return True, p
        # Add event adds an event to the event queue in order to be executed. 
        self.add_event(ev_open_page)
        
        # Now we add another event that will wait until the page is loaded. Note that we
        # don't use waiters here, because we don't want to block the execution of others
        # Pirate instances.
        # So if the following event return False (if the page is not loaded), it will be queued
        # again and executed some time before (in the next cicle).
        # In this case we use a callback to parse the information returned by get_loaded_page and
        # return a tuple (boolean, result_data)
        self.add_event(self.page.get_loaded_page,
                       callback=lambda x: (x is not None, x))
        
        def ev_get_title():
            title = self.page.evaluate("document.title")
            
            # Every time that one event it's executed successfully (it returns True)
            # The result_data will be saved into a private variable called (_last_result).
            # That result information can be retrived with "get_result", It has to be a
            # dictionary that can be converted to a json.
            return True, dict(title=unicode(title))
        self.add_event(ev_get_title)
        
    def start(self,  data):
        # We don't do anything with the data in this example
        self._add_events()
            
    def get_result(self):
        return self._last_result

# We define the main intance of ghost that we want to run
gh = Ghost(display=True,
            cache_size=10000,
            wait_timeout=30,
            prevent_download=["jpg", "png", "gif"],
            download_images=False,
            individual_cookies=True)

# Run Black Pearl Server
blackPerl = BlackPearl(gh, GhostWork)
blackPerl.start()
