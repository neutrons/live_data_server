=============================================
Configure for Local Debugging and Development
=============================================

If you just follow the steps in the readme then you will be able to start the service
but will not be able to interact with the api at all beyond receiving 400 errors.

In order to enable the api you will need to tweak some config settings.
(Maybe in the future it would be worth including these as dev versions)

docker-compose.yml
------------------

.. code-block:: yaml

    # replace this
    image: live_data:dev
    # with this
    build:
        network: host
        context: .


This will build from our local source instead of pulling an image online.


Settings.py
-----------

.. code-block:: python

    # replace this
    ALLOWED_HOSTS = ['livedata.sns.gov']
    # with this
    ALLOWED_HOSTS = ['*']



This setting is meant for production where its actually hosted on livedata.sns.gov.
Changing it to a wildcard lets us ping it as local host and not get a 400 error.


You should now be able to interact with the api on `localhost:9999` but there's a little more.
You need to add a user that you can use for your post requests,

.. code-block:: bash

    docker exec -it live_data_server_livedata_1 /bin/bash
    cd live_data_server
    python manage.py createsuperuser


I personally recommend using `Postman <https://www.postman.com/>`_ when interacting with the api.
If you do, set the request body to `form-data`!

Some relevant form-data field keys:

#. file
#. username
#. password
#. data_id
