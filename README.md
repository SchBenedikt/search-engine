# search-engine
The matching search engine to my [web crawler](https://github.com/SchBenedikt/web-crawler).

The Docker image is currently not working.
https://hub.docker.com/r/schbenedikt/search

## Features
- Display of the search speed.
- Ask AI for help.
- Uses MongoDB for database operations.
- Integration with Google search results.

## Docker Instructions

### Building the Docker Image

To build the Docker image, run the following command in the root directory of the repository:

```sh
docker build -t ghcr.io/schbenedikt/search-engine:latest .
```

### Running the Docker Container

To run the Docker container, use the following command:

```sh
docker run -p 5560:5560 ghcr.io/schbenedikt/search-engine:latest
```

This will start the Flask application using Gunicorn as the WSGI server, and it will be accessible at `http://localhost:5560`.

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

This will start both containers and the Flask application will be accessible at `http://localhost:5560`.

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
      - "5560:5560"

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

volumes:
  mongo-data:
```

### Database Configuration

The `db_config.json` file is used to store the database configuration. Here is an example of the `db_config.json` file:

```json
[
  {
    "url": "mongodb://localhost:27017",
    "name": "search_engine",
    "username": "your_username",
    "password": "your_password"
  }
]
```

### Settings Page

The `settings.html` file has been updated to include fields for username and password. You can access the settings page at `http://localhost:5560/settings` to update the database configuration.

## Making MongoDB Accessible from the Internet

### Using fritz.box for Port Forwarding

1. Log in to your fritz.box router by entering `http://fritz.box` in your web browser.
2. Navigate to the "Internet" section and then to "Permit Access".
3. Click on "Add Device for Sharing".
4. Select the device running MongoDB from the list.
5. Set the application to "Other Application" and enter the following details:
   - Protocol: TCP
   - From port: 27017
   - To port: 27017
6. Click "OK" to save the settings.

### Using Cloudflare Tunnel

1. Sign up for a Cloudflare account if you don't have one.
2. Go to the "Zero Trust" dashboard in Cloudflare.
3. Navigate to "Access" and then to "Tunnels".
4. Click on "Create a Tunnel".
5. Follow the instructions to install the Cloudflare Tunnel client on your server.
6. Create a new tunnel and configure it to forward traffic to your MongoDB instance on port 27017.
7. Update your MongoDB connection URL to use the Cloudflare Tunnel endpoint.
