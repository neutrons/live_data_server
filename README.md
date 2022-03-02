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


## Test & Verification

There is no direct verification of functionality for the containerized live-data-server container due to its design.
You can verify that the service is running by going to `localhost:9999/admin` after starting the application with `docker-compose up`.
The log info should tell you that the live-data-server is properly initializing the database as well as the 400 error when trying to access `localhost:9999/admin`.