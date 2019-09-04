# Machine Learning for Automated Vulnerability Detection in Source Code
*Masters Project at University of Bristol*

All of our code can be found in the [code](./code/) folder. Files are individually documented, while the [README.md](code/README.md) file guides you through the narrative and ordering of the project. The data used in this project can be found in [data](./data/). Generated figures and images can be found in [images](./images/).

Most of the code should run in our Docker environment (see `Development" below for setup details), with the exception of:

  1. Progol :: There is a working Progol in the Docker image (available in the `/progol/` directory). However, to repeat our results, our scripts should be ran on BlueCrystal using CProgol 4.4 compiled with GCC 5.4.
  2. Aleph :: We do not have redistribution rights for the ILP system we used.


## Development

We use `git-lfs` for storing larger files (primarily those in the ./data/ and ./images/ directories). This means that you need `git-lfs` installed before running `git clone`. See [this guide](https://www.atlassian.com/git/tutorials/git-lfs) for more info. If you get errors loading `csv` files into Pandas, it's probably a problem with `git-lfs`. Further, if there are errors when `git-lfs` is pulling files, it might be because we've ran out of bandwidth on this account, please get in touch with Dan (dj311) and he'll fix it.

Use [Docker](https://www.docker.com/) to get a working development environment. The easiest way is to pull down the latest build from docker hub via:

```sh
docker pull djwj/uob-summer-project
```

The above Docker repo isn't public, but send Dan(dj311 on Github) a message with your Docker Hub username and I'll give you permissions. The access control is to avoid accidentally leaking files which are not public.

Once the image is pulled,  run the container in the directory where you've cloned this repo, via:

  - `docker run --rm --name uob-summer-project --volume $PWD:/project --publish 8888:8888 --interactive --tty djwj/uob-summer-project`
  
The above command will start a Jupyter server. If you need a shell, you can exec into the container with `docker exec -it uob-summer-project /bin/bash`. That's an easy way to run Prolog or similar.


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

