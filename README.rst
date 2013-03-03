Ghost.py
========

Ghost.py is a webkit web client written in python


Example
-------
::

    from ghost import Ghost
    ghost = Ghost()
    page, extra_resources = ghost.open("http://jeanphi.fr")
    assert page.http_status==200 and 'jeanphix' in ghost.content


Full Documentation
------------------
The full documentation can be find in the following link 

* http://carrerasrodrigo.github.com/Ghost.py/

Alternative Branch
------------------
Now I'm working into a big restructuration of Ghost.py into the "multiple_tabs" brand. This branch improves problems like speed, memory and concurrency.
If you want to see the changes please referer to the following wiki:
* https://github.com/carrerasrodrigo/Ghost.py/wiki/About-the-changes-made-to-Ghost.py
