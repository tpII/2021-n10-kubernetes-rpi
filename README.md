# Docker MySQL Node Sequelize React boilerplate project

This is a boilerplate Docker project that:

1. Starts a MySQL server container based on the [official image](https://hub.docker.com/_/mysql/),
2. Starts a [Node.js 10.8.0](https://hub.docker.com/_/node/) app that waits for the database to become responsive, and run all migrations and seeds if necessary,
3. Starts a React app (also based on [Node.js 10.8.0](https://hub.docker.com/_/node/)).

You only need to have [Docker](https://www.docker.com/) installed in your computer, nothing else.
The docker-compose.yml file creates a bind mount directoty that allows you to test anything live, just change the code for the server or client and it will immediately become available.

The data for the MySQL will persist between launches.

To bring the project up first [install Docker](https://www.docker.com/), then run:

```
docker-compose up
```

The docker-compose.yml file routes port 80 on your host to the React app running on 3000 on the Docker environment, so once the system is up just go to http://localhost.

To bring it down:

```
docker-compose down
```

If you change your Dockerfile and must rebuild the Node.js or React images, run:

```
docker-compose up --build
```
