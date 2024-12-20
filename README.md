This repository works on top of ag2 (https://github.com/ag2ai/ag2/).  First pull or clone that repository.  Then use the files in this repsository in the main directory.
cd and use the dev docker file in ag2/.devcontainer/ directory
build the docker image through docker build -f dev/Dockerfile -t ag2_dev_img .
run the docker image to create the container.
once in the container simpley run
  python metagen.py
you will see options to list, describe, run and build orchestrations.
