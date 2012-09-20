.. Ghost.py documentation master file, created by
   sphinx-quickstart on Tue Sep 18 20:44:29 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About Ghost.py
====================================

This documentation corresponds to the version of Ghost.py in the following branch
https://github.com/carrerasrodrigo/Ghost.py manteined by Rodrigo Nicolas Carreras

Ghost.py is originally created by Jean-Philippe Serafin. I made a fork of his branch and
I implemented different functionalities since then. 

Ghost.py is a Webkit based scriptable web browser for python. It brings you all the
power of WebKit with an api in Python.


Installation
====================================

First you need to install **PyQt** or **PySide**. This will require to install the QT framework first.
You can find PyQt in the following link http://www.riverbankcomputing.com/software/pyqt/download

Then you need to install Ghost.py and flask for the testing.

Installing Flask::

    pip install Flask


For Ghost.py::
    
    pip install -e git+git://github.com/carrerasrodrigo/Ghost.py.git#egg=Ghost.py
    
or alternatively::

    git clone git://github.com/carrerasrodrigo/Ghost.py.git
    cd Ghost.py
    python setup.py install 

Easy peasy!


Examples
====================================

Let's search some planes on ebay::
    
    from ghost import Ghost

    url = "http://www.ebay.com/"
    gh = Ghost()

    # We load the main page of ebay
    page, resources = gh.open(url, wait_onload_event=True)

    # Full the main bar and click on the search button
    gh.set_field_value("#gh-ac", "plane")
    gh.click("#gh-btn")

    # Wait for the next page
    gh.wait_for_selector("#e1-15")

    # Save the image of the screen
    gh.capture_to("plane.png")


Some times we need to scrap a website but we don't need to download
css or js content. This Branch of Ghost.py has many improvements to make your
experience faster than ever. Let's see another example::

    from ghost import Ghost
    
    url = "http://news.ycombinator.com/"
    # We enable the cache and set the maximun size to 10 MB
    # We don't want to load images and load css or js files
    gh = Ghost(cache_size=10, download_images=False,
               prevent_download=["css", "js"])
    
    # wait_onload_event will tell to Ghost to leave the open method
    # when the On Ready event on the web page has been fired
    page, resources = gh.open(url, wait_onload_event=False)
    
    # We retrive the links from the web page
    links = gh.evaluate("""
                            var links = document.querySelectorAll("a");
                            var listRet = [];
                            for (var i=0; i<links.length; i++){
                                listRet.push(links[i].href);
                            }
                            listRet;
                        """)
    # Print the links
    for l in links[0]:
        print l


Ghost.py Class
====================================
Contents:

.. toctree::
   :maxdepth: 2
    
.. automodule:: ghost
 
.. autoclass:: Ghost
    :members: 


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
