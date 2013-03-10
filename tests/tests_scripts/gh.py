from ghost import Ghost

gh = Ghost("")
page, content = gh.open("http://news.ycombinator.com/")

gh.capture_to("/tmp/hackers_new.png")