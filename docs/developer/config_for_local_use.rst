=============================================
Configure for Local Debugging and Development
=============================================

Clone the repository and ``cd`` into the project directory.

Create a conda environment ``livedata``, containing all the dependencies

.. code-block:: python

  conda env create -f environment.yml
  conda activate livedata

To deploy this application locally, you will need to set a number of environment variables,  
for example (bash):

.. code-block:: bash

  export DATABASE_NAME=livedatadb
  export DATABASE_USER=livedatauser
  export DATABASE_PASS=livedatapass
  export DATABASE_HOST=db
  export DATABASE_PORT=5432
  export LIVE_PLOT_SECRET_KEY="secretKey"

  # These need to be set for `pytest`,
  # but are not used in the docker compose
  export DJANGO_SUPERUSER_USERNAME=$DATABASE_USER
  export DJANGO_SUPERUSER_PASSWORD=$DATABASE_PASS


*NOTES*:

- The ``DATABASE_PORT`` **must** be set to ``5432``, as Postgres is configured to listen on that port by default.  
  If you need to change the port, you will need to modify the ``docker-compose.yml`` file accordingly.

- It is recommended to save these variables into an ``.envrc`` file which can be managed by `direnv <https://direnv.net/>`_.  
  direnv will automatically load the variables when you ``cd`` into the project directory.

After the secrets are set, you can start the server with:

.. code-block:: bash

  make local/docker/up

This command will copy ``config/docker-compose.envlocal.yml`` into ``./docker-compose.yml`` before composing all the services.

| Run ``make help`` to learn about other macros available as make targets.  
| For instance, ``make docker/pruneall`` will stop all containers, then remove all containers, images, networks, and volumes.

Testing
-------

After the setup, with the server running, you can test your setup with ``pytest``:

.. code-block:: bash

  # run all tests
  pytest
  # or run a specific test
  pytest tests/test_post_get.py

*NOTE:*  
The environment variables ``DJANGO_SUPERUSER_USERNAME`` and ``DJANGO_SUPERUSER_PASSWORD`` are defined in the ``docker-compose.envlocal.yml`` file, but ``pytest`` does not read this file.  
You must either have them exported to the shell where ``pytest`` is to be run, as described above, or modify the ``pytest`` command to include them, e.g.:

.. code-block:: bash

  DJANGO_SUPERUSER_USERNAME=***** DJANGO_SUPERUSER_PASSWORD=***** pytest

API
---

I personally recommend using `Postman <https://www.postman.com/>`_ when interacting with the api.
If you do, set the request body to ``form-data``!

Some relevant form-data field keys: 

#. file
#. username
#. password
#. data_id
