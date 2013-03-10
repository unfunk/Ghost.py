from ghost import Ghost
from ghost.NetworkMonitor import NetworkMonitor
import json

class NM(NetworkMonitor):
    pass

gh = Ghost(network_monitor=NM)

page, resources = gh.open("http://www.lanacion.com.ar")

print "test"
data =  json.dumps(gh.get_network_monitor().dump())
gh.get_network_monitor().reset()
with open("/tmp/har2.har", "w") as f:
    f.write(data)




