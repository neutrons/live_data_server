## live_data_server
Data server for data plots


## Contributing

Create a conda environment `livedata`, containing all the dependencies 
```python
conda env create -f environment.yml
conda activate livedata
```

### Containerization

To deploy this application locally for development you will need to have the following secrets
as environment variables defined in the shell's environment:
```bash
      DATABASE_NAME
      DATABASE_USER
      DATABASE_PASS
      DATABASE_HOST
      DATABASE_PORT
      LIVE_PLOT_SECRET_KEY
```
You can contact a member of the development team to obtain sensible values for these variables.
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

There is no direct verification of functionality for the containerized live-data-server
container due to its design.
You can verify that the service is running by going to `localhost:9999/admin` after
starting the application with `docker-compose up`.
The log info should tell you that the live-data-server is properly initializing the database
as well as the 400 error when trying to access `localhost:9999/admin`.

## Deployment to the Test Environment
- Repository managing the provision for deployment:
  + hardware and networking for deployment: https://code.ornl.gov/sns-hfir-scse/infrastructure/neutrons-test-environment/-/blob/main/terraform/servers.tf#L85-97
  + configuration independent of source code changes: https://code.ornl.gov/sns-hfir-scse/infrastructure/neutrons-test-environment/-/blob/main/ansible/testfixture02-test.yaml
- Repository managing deployment of the source to the provisioned hardware: https://code.ornl.gov/sns-hfir-scse/deployments/livedata-deploy
