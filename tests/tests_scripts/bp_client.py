import urllib
from threading import Thread
th = []

def post_to_ghost():
    # We communicate with Black Pear with a POST request.
    data = dict(data="some data")
    content = urllib.urlopen("http://localhost:5000/work", urllib.urlencode(data))
    print content.read()
    
# We run 20 requests
for i in range(20):
    thread = Thread(target=post_to_ghost)
    thread.start()
    th.append(thread)

# We wait until all the thread finished their work
for t in th:
    t.join()
