from ghost import Ghost

url = "http://news.ycombinator.com/"
# We enable the cache and set the maximun size to 10 MB
# We don't want to load images and load css or js files
gh = Ghost(cache_size=10)

# We create a new page
page, page_name = gh.create_page(download_images=False,
        prevent_download=["css", "js"])

# wait_onload_event will tell to Ghost to leave the open method
# when the On Ready event on the web page has been fired
page_resource = page.open(url, wait_onload_event=False)

# We retrive the links from the web page
links = page.evaluate("""
                        var links = document.querySelectorAll("a");
                        var listRet = [];
                        for (var i=0; i<links.length; i++){
                            listRet.push(links[i].href);
                        }
                        listRet;
                    """)
# Print the links
for l in links:
    print l