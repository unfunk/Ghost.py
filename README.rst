Ghost.py
========

Ghost.py is a webkit web client written in python


Example
-------
::

    from ghost import Ghost
    ghost = Ghost()
    page, page_name = ghost.open("http://jeanphi.fr")
    assert page.http_status==200 and 'jeanphix' in ghost.content


Full Documentation
------------------
The full documentation can be find in the following link 

* http://carrerasrodrigo.github.com/Ghost.py/

Alternative Branch
------------------
This branch has a **big restructuration** of Ghost.py. Improve problems like speed, memory and concurrency.
If you want to see the changes please referer to the following wiki:

* https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py

History
-------
10/03/2013
 - Big Restructuration in Ghost.py Core [More info] (https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py)
 - Added support for multiple tabs. [More info] (https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py) - [Example] (https://github.com/carrerasrodrigo/Ghost.py/wiki/Example----Multiple-Tabs)
 - Added a solution for concurrent tabs (Black Pearl Server) [More info] (https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py)

Past changes
- Support for Popups
- Support for Fast Open [Example] (https://github.com/carrerasrodrigo/Ghost.py/wiki/Example---Fast-Open)
- Sopport for selective download [Example] (https://github.com/carrerasrodrigo/Ghost.py/wiki/Example---Selective-Download)
- Support for cache [Example] (https://github.com/carrerasrodrigo/Ghost.py/wiki/Example---Cache)
- Added new method to switch beetween frames.
- Added the option to capture an image from the webpage an save it into a PDF file.
- Added support for connection via proxy
- Added a "download" method that save the webpage content into a file.
