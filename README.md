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
docker build -t search-engine .
```

### Running the Docker Container

To run the Docker container, use the following command:

```sh
docker run -p 5000:5000 search-engine
```

This will start the Flask application, and it will be accessible at `http://localhost:5000`.
