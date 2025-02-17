# search-engine
The matching search engine to my [web crawler](https://github.com/SchBenedikt/web-crawler).

The Docker image is currently being developed further.
https://hub.docker.com/r/schbenedikt/search

## Features
- Like Projects (The most liked pages are displayed at the top)
- Display of the search speed.
- Ask AI for help.
- Uses MongoDB for database operations.

## Docker Instructions

### Building the Docker Image

To build the Docker image, run the following command in the root directory of the repository:

```sh
docker build -t ghcr.io/schbenedikt/search-engine:latest .
```

### Running the Docker Container

To run the Docker container, use the following command:

```sh
docker run -p 5000:5000 ghcr.io/schbenedikt/search-engine:latest
```

This will start the Flask application using Gunicorn as the WSGI server, and it will be accessible at `http://localhost:5000`.

### Pulling the Docker Image

The Docker image is publicly accessible. To pull the Docker image from GitHub Container Registry, use the following command:

```sh
docker pull ghcr.io/schbenedikt/search-engine:latest
```

### Note
Ensure that the `tags` field in the GitHub Actions workflow is correctly set to `ghcr.io/schbenedikt/search-engine:latest` to avoid multiple packages.

### Running with Docker Compose

To run both the search engine and MongoDB containers using Docker Compose, use the following command:

```sh
docker-compose up
```

This will start both containers and the Flask application will be accessible at `http://localhost:5000`.

### Docker Compose File

The `docker-compose.yml` file is used to manage both the search engine and MongoDB containers. Here is an example of the `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  search-engine:
    image: ghcr.io/schbenedikt/search-engine:latest
    depends_on:
      - mongodb
    ports:
      - "5000:5000"

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```
