# live_data_server

<!-- Badges -->

[![Documentation Status](https://readthedocs.org/projects/livedata-ornl/badge/?version=latest)](https://livedata-ornl.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/neutrons/live_data_server/graph/badge.svg?token=niQ0AWldBd)](https://codecov.io/gh/neutrons/live_data_server)

Data server for data plots.

Developer documentation at https://livedata-ornl.readthedocs.io/en/latest/

## Development

### Dependencies

- [Conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) / [Mamba]()
- [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [direnv](https://direnv.net/) (optional)

### Setup for Local Development

Clone the repository and `cd` into the project directory.

Create a conda environment `livedata`, containing all the dependencies
```python
conda env create -f environment.yml
conda activate livedata
```

To deploy this application locally, you will need to set a number of environment variables,  
for example (bash):

```bash
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
```

**Notes**:

- The `DATABASE_PORT` _must_ be set to `5432`, as Postgres is configured to listen on that port by default.  
  If you need to change the port, you will need to modify the `docker-compose.yml` file accordingly.

- It is recommended to save these variables into an `.envrc` file which can be managed by [direnv](https://direnv.net/).  
  direnv will automatically load the variables when you `cd` into the project directory.

After the secrets are set, type in the terminal shell:

```bash
make local/docker/up
```

This command will copy `config/docker-compose.envlocal.yml` into `docker-compose.yml` before composing all the services.

Type `make help` to learn about other macros available as make targets.  
For instance, `make docker/pruneall` will stop all containers, then remove all containers, images, networks, and volumes.

### Testing

After the setup, with the server running, you can test your setup by running `pytest`:

```bash
pytest tests/test_post_get.py
# or simply
pytest
```

**NOTE:**  
The environment variables `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` are defined in the `docker-compose.envlocal.yml` file, but `pytest` does not read this file.  
You must either have them exported to the shell where `pytest` is to be run, as described above, or modify the `pytest` command to include them, e.g.:

```bash
DJANGO_SUPERUSER_USERNAME=***** DJANGO_SUPERUSER_PASSWORD=***** pytest
```

## Deployment to the Test Environment

- Repository managing the provision for deployment:
  - hardware and networking for deployment: https://code.ornl.gov/sns-hfir-scse/infrastructure/neutrons-test-environment/-/blob/main/terraform/servers.tf#L85-97
  - configuration independent of source code changes: https://code.ornl.gov/sns-hfir-scse/infrastructure/neutrons-test-environment/-/blob/main/ansible/testfixture02-test.yaml
- Repository managing deployment of the source to the provisioned hardware: https://code.ornl.gov/sns-hfir-scse/deployments/livedata-deploy

## Building the Documentation

Additional documentation is available in the `docs` directory. To build the documentation in your local machine,
run the following command from within directory `docs/`:

```bash
make html
```

The documentation will be built in the `docs/_build/html` directory. To view the documentation,
open the `docs/_build/html/index.html` file in a web browser.
