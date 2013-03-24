Ghost.py
========

Ghost.py is a webkit web client written in python


Example
-------
::

    from ghost import Ghost
    gh = Ghost()
    gpage, name = gh.create_page()
    gpage.open("http://www.google.com")
    gpage.capture_to("/tmp/google.png")


Full Documentation
------------------
The full documentation can be found in the following link 

* http://carrerasrodrigo.github.com/Ghost.py/

Alternative Branch
------------------
This branch has a **big restructuration** of Ghost.py. Improve problems like speed, memory and concurrency.
If you want to see the changes please referer to the following wiki:

* https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py

History
-------
**24/03/2013**
 - Added the option to redirect Qt Framework messages to python logging system. Based on pull request https://github.com/jeanphix/Ghost.py/pull/70 . Thanks to @asdil12
::

    #How to enable debug messages (QT included)
    import logging
    gh = Ghost(qt_debug=True, log_level=logging.DEBUG)
    
    ... Do Something else with ghost
 
**21/03/2013**
 - Patch that solve bug #12 for PySide https://github.com/carrerasrodrigo/Ghost.py/issues/12

**15/03/2013**
 - Added two methods in to GhostWebPage, load_cookie and save_cookie.
 - Added support for java and plugins based on commit https://github.com/jeanphix/Ghost.py/commit/18686b654e02e0406bd85a2c09cd938a07c5303d (Thanks to @jansel)
 - Changed method captured_to. Now it renders the whole page based on commit https://github.com/asdil12/Ghost.py/commit/5630b42e49aa74918fe9a9d4023183d74346471b (Thanks to @asdil12) `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/Examples---Useful-Examples>`_
 - Fix test cases. Removed unused methods. 

**10/03/2013**
 - Big Restructuration in Ghost.py Core `More info <https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py>`_
 - Added support for multiple tabs. `More info <https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py>`_ -  `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py>`_
 - Added a solution for concurrent tabs (Black Pearl Server) `More info <https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py>`_

**Past changes**

- Support for Popups
- Support for Fast Open `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/Example---Fast-Open>`_

- Sopport for selective download `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/Example---Selective-Download>`_
- Support for cache `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/Example---Cache>`_
- Added new method to switch beetween frames.
- Added the option to capture an image from the webpage and save it into a PDF file `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/Examples---Useful-Examples>`_
- Added support for connection via proxy
- Added a "download" method that save the webpage content into a file `Example <https://github.com/carrerasrodrigo/Ghost.py/wiki/Examples---Useful-Examples>`_
