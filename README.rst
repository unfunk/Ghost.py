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

