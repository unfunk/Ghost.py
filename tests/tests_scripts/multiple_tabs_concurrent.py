from ghost import Ghost
import time

# Creates a Ghost instance telling to share cache and don't share cookies
gh = Ghost(share_cache=True, share_cookies=False)
page1, name = gh.create_page()
page2, name = gh.create_page()

# Open google
page1.open("http://www.google.com", wait_for_loading=False)

# Open Hacker News
page2.open("http://news.ycombinator.com/", wait_for_loading=False)

# At this point ghost it's rendering the two pages at the same time. Now we
# need to check if the pages are loaded.
while page1.get_loaded_page() is None:
    page_resource = page1.get_loaded_page()
    gh.process_events()
    time.sleep(0.01)
    
# Saves an image of the screen 1
page1.capture_to("/tmp/tab1.png")
print "open /tmp/tab1.png"


#Or we can use wait_for_page_loaded() instead
page2.wait_for_page_loaded()

# Saves an image of the screen 2
page2.capture_to("/tmp/tab2.png")
print "open /tmp/tab2.png"

# Then we remove the tabs from ghost instance
gh.remove_page(page1)
gh.remove_page(page2)
