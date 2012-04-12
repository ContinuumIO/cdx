============
 CloudBlaze
============
This is the web project for continuum, a frontend for our fast platform for array computations and analytics, Numpy Blaze!

================
 Project Layout
================
all code in src:

blazeweb - web api for numpy blaze
continuumweb - common code for all of continuum's future web projects.  Currently this only contains the webzmqproxy.  

==============
 Dependencies
==============
gevent_zeromq
zeromq
flask

only for tests:
     nosetest
     requests 

=========
 Testing
=========
go to src
run nosetests


