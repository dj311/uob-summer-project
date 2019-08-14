# Machine Learning for Automated Vulnerability Detection in Source Code <small>(WIP)</small>
*Masters Project at University of Bristol*

All of our documented code can be found in the [code](./code/) folder. The data used in this project can be found in the [data](./data/) folder. Generated figures and images can be found in the [images](./images/) folder.


## Development

Use [Docker](https://www.docker.com/) to get a working development environment. The easiest way is to pull down the latest build from docker hub via:

```sh
docker pull djwj/uob-summer-project
```

The above Docker repo isn't public, but send dj311 a message (on Github) with your Docker Hub username and I'll give you permissions. Once the image is pulled,  run the container from the same directory as this file, via:

  - `docker run --name uob-summer-project --volume $PWD:/project --publish 8888:8888 --interactive --tty djwj/uob-summer-project` to start a Jupyter server.
  
If you need a shell, you can exec in with `docker exec -it uob-summer-project /bin/bash` or whatever your favourite shell is.
  


### Adding New Dependencies
First, add them to the right place depending on their type:

  - Python dependencies can be added to the [requirements.txt](./requirements.txt).
  - Add native libraries via the `apt install ...` line in the [Dockerfile](./Dockerfile).

Next, the Docker image needs to be rebuilt, then pushed up to the docker hub. Do this via:

```sh
docker build --tag djwj/uob-summer-project .
docker push djwj/uob-summer-project
```

If the second command complains about permissions, you probably need to:

  1. Ensure you have an account on [Docker Hub](https://hub.docker.com).
  2. Get yourself added as a contributor to the [uob-summer-project repository](https://docker.io/djwj/uob-summer-project).
  3.  Sign into the account on the command line via `docker login`.

