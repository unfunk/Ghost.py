from ghost import Ghost

# Here we create a ghost instance with cache in /tmp/ghost.py and a max size of 10 MB.
# We also indicates that the cache folder would be shared between tabs 
gh = Ghost(cache_dir="/tmp/ghost.py", cache_size=10, share_cache=True)
gpage, name = gh.create_page(download_images=True, prevent_download=["css"])

# Open google
gpage.open("http://www.google.com")
