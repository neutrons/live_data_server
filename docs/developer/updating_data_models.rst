=============================================
Updating Data Models
=============================================

| There may be times when you need to update the data models used by Django.
| This can be done by following these steps:

#. Make the necessary changes to the models in ``src/apps/plots/models.py``.
#. Generate the Django migration file(s):

   .. code-block:: bash

      cd src
      python manage.py makemigrations

The migration(s) will be created in the ``src/apps/plots/migrations/`` directory.
First check the migration(s) to ensure they are correct. If they are, apply the migration(s):

From within the Django app Docker container:

.. code-block:: bash

   python manage.py migrate

   # or if you are not in the container
   docker exec -i live_data_server-django-1 bash -ic '
      conda activate livedata
      cd app
      python manage.py migrate
      '

If the migration(s) are not correct, you can delete them and start again:

.. code-block:: bash

   python manage.py migrate plots zero
   python manage.py makemigrations
   python manage.py migrate
