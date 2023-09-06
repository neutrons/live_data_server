======================
Service Through Apache
======================

.. contents::
    :local:

As of this day (September 3, 2023), the live data service is hosted in livedata.sns.gov. The version of the
service corresponds to `refspec 78ef6ad9b237274ac63c69b99d334657ac373633 <https://github.com/neutrons/live_data_server/tree/78ef6ad9b237274ac63c69b99d334657ac373633>`_.
At this point, docker containerization had not been implemented yet, and the application is served through the
Apache HTTP Server.

The `Apache configuration file <https://github.com/neutrons/live_data_server/blob/78ef6ad9b237274ac63c69b99d334657ac373633/apache/apache_django_wsgi.conf>`_
is located at ``/etc/httpd/conf.d/apache_django_wsgi.conf``, and the application is located in
``/var/www/livedata/app``.



