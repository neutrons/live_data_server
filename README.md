## live_data_server
Data server for data plots


## Contributing

Create a conda environment `livedata`, containing all the dependencies 
```python
conda env create -f environment.yml
conda activate livedata
```

### Containerization

To deploy this application locally for development you will need to assign values to the following secrets
as environment variables defined in the shell's environment:
```bash
      DATABASE_NAME
      DATABASE_USER
      DATABASE_PASS
      DATABASE_HOST
      DATABASE_PORT
      LIVE_PLOT_SECRET_KEY
```
It is recommended to save these variables into an `.envrc` file which can be managed by
[envdir](https://direnv.net/).

After the secrets are set, type in the terminal shell:
```bash
make local/docker/up
```
This command will copy `config/docker-compose.envlocal.yml` into `docker-compose.yml` before composing
all the services.

Type `make help` to learn about other macros available as make targets.
For instance, `make docker/pruneall` will stop all containers, then remove
all containers, images, networks, and volumes.

## Test & Verification

After starting the services with `make local/docker/up`, run the test that will post and get data:

```bash
DJANGO_SUPERUSER_USERNAME=***** DJANGO_SUPERUSER_PASSWORD=***** pytest tests/test_post_get.py
```

Environment variables `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` are defined in
file `docker-compose.envlocal.yml`. You need to either pass these variables with the correct values or have
them exported to the shell where `pytest` is to be run.

## Deployment to the Test Environment
- Repository managing the provision for deployment:
  + hardware and networking for deployment: https://code.ornl.gov/sns-hfir-scse/infrastructure/neutrons-test-environment/-/blob/main/terraform/servers.tf#L85-97
  + configuration independent of source code changes: https://code.ornl.gov/sns-hfir-scse/infrastructure/neutrons-test-environment/-/blob/main/ansible/testfixture02-test.yaml
- Repository managing deployment of the source to the provisioned hardware: https://code.ornl.gov/sns-hfir-scse/deployments/livedata-deploy


## Building the Documentation
Additional documentation is available in the `docs` directory. To build the documentation in your local machine,
run the following command from within directory `docs/`:
```bash
make html
```
The documentation will be built in the `docs/_build/html` directory. To view the documentation,
open the `docs/_build/html/index.html` file in a web browser.