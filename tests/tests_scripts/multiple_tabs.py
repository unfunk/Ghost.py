from ghost import Ghost

# Creates a Ghost instance telling to share cache and don't share cookies
gh = Ghost(share_cache=True, share_cookies=False)
page1, name = gh.create_page()
page2, name = gh.create_page()

# Open google
page1.open("http://www.google.com")

# Open Hacker News
page2.open("http://news.ycombinator.com/")

# Saves an image of the screen 1
page1.capture_to("/tmp/tab1.png")
print "open /tmp/tab1.png"

# Saves an image of the screen 2
page2.capture_to("/tmp/tab2.png")
print "open /tmp/tab2.png"

# Then we remove the tabs from ghost instance
gh.remove_page(page1)
gh.remove_page(page2)
