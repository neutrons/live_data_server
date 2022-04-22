## live_data_server
Data server for data plots

## Containerization

The provided Dockerfile can be used to generated an image that contains the application (un-initialized state).
To deploy this application locally for development, there are two options:

- Use the provided `docker-compose.yml` file to start a local private docker network where a postgresql database and the livedata application is served.
- Add the image to other `docker-compose.yml` where live-data-server is needed
  - make sure the other `docker-compose.yml` has a working database instance running before the live-data-server
  - make sure modify the database instance script to include the creation of the table needed by live-data-server
  - make sure passing the database related environment variables into the live-data-server container.

## Contributing

Create conda environment `livedata`, containing all the requirements 
```python
conda env create -f environment.yml
conda activate livedata
```

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
