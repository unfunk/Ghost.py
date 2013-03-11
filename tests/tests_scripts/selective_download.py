from ghost import Ghost

# Creates a Ghost instance telling to don't download css files and images
gh = Ghost()
gpage, name = gh.create_page(download_images=True, prevent_download=["css"])

# Open google
gpage.open("http://www.google.com")

# Saves an image of the screen
gpage.capture_to("/tmp/selective_download.png")

